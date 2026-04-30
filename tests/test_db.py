from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session, mock_db_time):

    with mock_db_time(model=User) as fake_time:
        new_user = User(
            username='alice', email='alice@example.com', password='supersecret'
        )

        session.add(new_user)
        session.commit()

        user = session.scalar(select(User).where(User.username == 'alice'))

    assert asdict(user) == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'supersecret',
        'created_at': fake_time,
        'updated_at': fake_time,
    }
