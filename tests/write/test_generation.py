import pandas as pd
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from pvsite_datamodel.sqlmodels import GenerationSQL
from pvsite_datamodel.write.generation import insert_generation_values


class TestInsertGenerationValues:
    """Tests for the insert_generation_values function."""

    def test_inserts_generation_for_existing_site(self, db_session, generation_valid_site):
        """Tests inserts values successfully."""
        df = pd.DataFrame(generation_valid_site)
        insert_generation_values(db_session, df)
        db_session.commit()
        # Check data has been written and exists in table
        assert db_session.query(GenerationSQL).count() == 10

    def test_errors_on_invalid_dataframe(self, engine, generation_invalid_dataframe):
        """Tests function errors on invalid dataframe."""
        df = pd.DataFrame(generation_invalid_dataframe)

        with Session(bind=engine) as session:
            num_rows = session.query(GenerationSQL).count()

            with session.begin_nested():
                with pytest.raises(SQLAlchemyError):
                    insert_generation_values(session, df)
                session.rollback()

            # Make sure nothing was written
            assert session.query(GenerationSQL).count() == num_rows

    def test_inserts_generation_duplicates(self, db_session, generation_valid_site):
        """Tests no duplicates."""
        df = pd.DataFrame(generation_valid_site)
        insert_generation_values(db_session, df)
        db_session.commit()
        # Check data has been written and exists in table
        assert db_session.query(GenerationSQL).count() == 10

        # insert the same values
        insert_generation_values(db_session, df)
        db_session.commit()
        assert db_session.query(GenerationSQL).count() == 10

    def tests_inserts_end_utc(self, db_session, generation_valid_end_utc):
        """Tests end_utc handled successfully."""
        df = pd.DataFrame(generation_valid_end_utc)
        insert_generation_values(db_session, df)
        db_session.commit()

        rows = db_session.query(GenerationSQL.start_utc, GenerationSQL.end_utc).all()
        # Check data has been written and exists in table
        assert len(rows) == 10

        # Check both start and end timestamps
        for idx, (stored_start, stored_end) in enumerate(rows):
            # Compare timestamps at the minute level to avoid timezone issues
            assert stored_start.strftime("%Y-%m-%d %H:%M") == generation_valid_end_utc["start_utc"][
                idx
            ].strftime("%Y-%m-%d %H:%M")
            assert stored_end.strftime("%Y-%m-%d %H:%M") == generation_valid_end_utc["end_utc"][
                idx
            ].strftime("%Y-%m-%d %H:%M")
