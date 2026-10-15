from app import database
from app.schemas import CarInput

def test_saved_car_can_be_read_from_sqlite(database_path):
    database.initialize(database_path)
    saved = database.create_car(
        database_path,
        CarInput(make="Toyota", model="Yaris", year=2020, color="Blue"),
    )
    loaded = database.get_car(database_path, saved.id)
    assert loaded is not None
    assert loaded.id == saved.id
    assert loaded.make == "Toyota"
    assert loaded.year == 2020
def test_deleting_one_car_keeps_the_other(database_path):
    database.initialize(database_path)
    saved1 = database.create_car(
        database_path,
        CarInput(make="BMW", model="M3", year=2018, color="Red"),
    )
    saved2 = database.create_car(
        database_path,
        CarInput(make="Audi", model="A4", year=2019, color="Black"),
    )
    database.delete_car(database_path, saved1.id)
    loaded1 = database.get_car(database_path, saved1.id)
    loaded2 = database.get_car(database_path, saved2.id)
    assert loaded1 is None
    assert loaded2 is not None
    cars = database.list_cars(database_path)
    assert len(cars) == 1
    assert cars[0].id == saved2.id