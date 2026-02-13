import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Ensure src is on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

def clear_db():
    try:
        from storage.database.db import get_session
        from storage.database.shared.model import Question, ExamPaper, ExamPaperQuestion

        session = get_session()
        try:
            deleted_epq = session.query(ExamPaperQuestion).delete()
            deleted_ep = session.query(ExamPaper).delete()
            deleted_q = session.query(Question).delete()
            session.commit()
            print(f"Cleared DB: exam_paper_questions={deleted_epq}, exam_papers={deleted_ep}, questions={deleted_q}")
        except Exception as e:
            session.rollback()
            print(f"Error clearing DB: {e}")
            raise
        finally:
            session.close()
    except Exception as e:
        print(f"Failed to clear DB (check PGDATABASE_URL and DB availability): {e}")
        raise

if __name__ == '__main__':
    clear_db()
