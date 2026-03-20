from dataclasses import asdict

from sqlalchemy import select

from projeto1.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='Taz', password='1234', email='taz@gmail.com')
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'Taz'))

    assert asdict(user) == {
        'id': 1,
        'username': 'Taz',
        'email': 'taz@gmail.com',
        'password': '1234',
        'created_at': time,
        'updated_at': time,
    }
