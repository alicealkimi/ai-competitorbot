"""SQLite database operations and schema initialization."""
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import config

logger = logging.getLogger(__name__)


def get_connection():
    """Get database connection."""
    db_path = Path(config.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            pub_date TEXT,
            full_text TEXT,
            processed_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Classifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            relevance_score INTEGER,
            category TEXT,
            product_impact TEXT,
            summary TEXT,
            llm_response TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    """)
    
    # Threat assessments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threat_assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            threat_level TEXT,
            product_impact TEXT,
            action_recommendation TEXT,
            reviewed_by TEXT,
            reviewed_at TEXT,
            FOREIGN KEY (article_id) REFERENCES articles(id),
            UNIQUE(article_id)
        )
    """)
    
    # Deliveries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_type TEXT NOT NULL,
            delivery_date TEXT NOT NULL,
            channel TEXT NOT NULL,
            message_id TEXT,
            articles_included TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_pub_date ON articles(pub_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_classifications_article_id ON classifications(article_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_threat_assessments_article_id ON threat_assessments(article_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_threat_assessments_reviewed_at ON threat_assessments(reviewed_at)")
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


def article_exists(url: str) -> bool:
    """Check if article with given URL already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def insert_article(headline: str, url: str, source: str, pub_date: Optional[str] = None, 
                   full_text: Optional[str] = None) -> int:
    """Insert a new article and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO articles (headline, url, source, pub_date, full_text)
            VALUES (?, ?, ?, ?, ?)
        """, (headline, url, source, pub_date, full_text))
        article_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Inserted article: {headline[:50]}...")
        return article_id
    except sqlite3.IntegrityError:
        logger.warning(f"Article already exists: {url}")
        cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
        result = cursor.fetchone()
        return result['id'] if result else None
    finally:
        conn.close()


def insert_classification(article_id: int, relevance_score: int, category: str,
                         product_impact: str, summary: str, llm_response: str) -> int:
    """Insert classification for an article."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO classifications (article_id, relevance_score, category, 
                                    product_impact, summary, llm_response)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (article_id, relevance_score, category, product_impact, summary, llm_response))
    classification_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.debug(f"Inserted classification for article {article_id}")
    return classification_id


def insert_threat_assessment(article_id: int, threat_level: str, product_impact: str,
                            action_recommendation: str, reviewed_by: str) -> int:
    """Insert or update threat assessment for an article."""
    conn = get_connection()
    cursor = conn.cursor()
    reviewed_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO threat_assessments 
        (article_id, threat_level, product_impact, action_recommendation, reviewed_by, reviewed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (article_id, threat_level, product_impact, action_recommendation, reviewed_by, reviewed_at))
    assessment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Inserted threat assessment for article {article_id}: {threat_level}")
    return assessment_id


def get_pending_reviews() -> List[Dict[str, Any]]:
    """Get articles with classifications but no threat assessment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.headline, a.url, a.source, a.pub_date,
               c.relevance_score, c.category, c.product_impact, c.summary
        FROM articles a
        INNER JOIN classifications c ON a.id = c.article_id
        LEFT JOIN threat_assessments t ON a.id = t.article_id
        WHERE t.id IS NULL
        ORDER BY c.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_reviewed_articles_for_digest(limit: int = 5) -> List[Dict[str, Any]]:
    """Get reviewed articles ready for daily digest."""
    conn = get_connection()
    cursor = conn.cursor()
    # Get articles reviewed today or yesterday that haven't been delivered yet
    cursor.execute("""
        SELECT a.id, a.headline, a.url, a.source, a.pub_date,
               c.summary, c.category, c.product_impact,
               t.threat_level, t.action_recommendation
        FROM articles a
        INNER JOIN classifications c ON a.id = c.article_id
        INNER JOIN threat_assessments t ON a.id = t.article_id
        WHERE t.reviewed_at >= date('now', '-2 days')
        AND a.id NOT IN (
            SELECT DISTINCT json_each.value
            FROM deliveries d
            WHERE d.delivery_type = 'daily_digest'
            AND d.delivery_date >= date('now', '-1 day')
            AND json_valid(d.articles_included)
        )
        ORDER BY 
            CASE t.threat_level
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
                WHEN 'OPPORTUNITY' THEN 4
                ELSE 5
            END,
            t.reviewed_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_weekly_stats(start_date: str, end_date: str) -> Dict[str, Any]:
    """Get statistics for weekly summary."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total articles scanned
    cursor.execute("""
        SELECT COUNT(*) as total FROM articles
        WHERE processed_at >= ? AND processed_at <= ?
    """, (start_date, end_date))
    total_scanned = cursor.fetchone()['total']
    
    # Relevant articles (with classifications)
    cursor.execute("""
        SELECT COUNT(DISTINCT a.id) as relevant
        FROM articles a
        INNER JOIN classifications c ON a.id = c.article_id
        WHERE a.processed_at >= ? AND a.processed_at <= ?
    """, (start_date, end_date))
    relevant = cursor.fetchone()['relevant']
    
    # High priority articles
    cursor.execute("""
        SELECT COUNT(*) as high_priority
        FROM threat_assessments
        WHERE threat_level = 'HIGH'
        AND reviewed_at >= ? AND reviewed_at <= ?
    """, (start_date, end_date))
    high_priority = cursor.fetchone()['high_priority']
    
    # Threat breakdown by product
    cursor.execute("""
        SELECT t.product_impact, COUNT(*) as count
        FROM threat_assessments t
        WHERE t.reviewed_at >= ? AND t.reviewed_at <= ?
        GROUP BY t.product_impact
    """, (start_date, end_date))
    product_breakdown = {row['product_impact']: row['count'] for row in cursor.fetchall()}
    
    # Threat breakdown by level
    cursor.execute("""
        SELECT t.threat_level, COUNT(*) as count
        FROM threat_assessments t
        WHERE t.reviewed_at >= ? AND t.reviewed_at <= ?
        GROUP BY t.threat_level
    """, (start_date, end_date))
    threat_breakdown = {row['threat_level']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        'total_scanned': total_scanned,
        'relevant': relevant,
        'high_priority': high_priority,
        'product_breakdown': product_breakdown,
        'threat_breakdown': threat_breakdown
    }


def record_delivery(delivery_type: str, delivery_date: str, channel: str,
                   message_id: Optional[str], articles_included: List[int]):
    """Record a delivery to track what was sent."""
    conn = get_connection()
    cursor = conn.cursor()
    articles_json = str(articles_included)  # Simple list representation
    cursor.execute("""
        INSERT INTO deliveries (delivery_type, delivery_date, channel, message_id, articles_included)
        VALUES (?, ?, ?, ?, ?)
    """, (delivery_type, delivery_date, channel, message_id, articles_json))
    conn.commit()
    conn.close()
    logger.info(f"Recorded {delivery_type} delivery to {channel}")

