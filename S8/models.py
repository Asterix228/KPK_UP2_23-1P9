from datetime import datetime
from peewee import (
    SqliteDatabase, Model, AutoField, CharField, IntegerField,
    ForeignKeyField, DateTimeField, BooleanField, Check
)

db = SqliteDatabase('subgroup.db')


class BaseModel(Model):
    class Meta:
        database = db


class Group(BaseModel):
    """Внешняя сущность: учебная группа (заглушка, управляется Group Service)"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=50, unique=True)

    class Meta:
        table_name = 'groups'


class Student(BaseModel):
    """Внешняя сущность: студент (заглушка, управляется Profile Service)"""
    id = AutoField(primary_key=True)
    full_name = CharField(max_length=150)
    group = ForeignKeyField(Group, backref='students', on_delete='RESTRICT')

    class Meta:
        table_name = 'students'


class Subgroup(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, constraints=[Check("length(name) >= 1")])
    group = ForeignKeyField(Group, backref='subgroups', on_delete='RESTRICT')
    purpose = CharField(max_length=200, null=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'subgroups'
        indexes = (
            (('name', 'group'), True),  # уникальная комбинация name + group_id
        )

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)


class SubgroupStudent(BaseModel):
    """Транзитивная таблица: связь многие ко многим между Subgroup и Student"""
    id = AutoField(primary_key=True)
    subgroup = ForeignKeyField(Subgroup, backref='subgroup_students', on_delete='CASCADE')
    student = ForeignKeyField(Student, backref='subgroup_students', on_delete='CASCADE')
    joined_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'subgroup_students'
        indexes = (
            (('subgroup', 'student'), True),  # студент может быть в подгруппе только один раз
        )


def init_db():
    """Создание таблиц и заполнение начальными данными"""
    db.connect()
    db.create_tables([Group, Student, Subgroup, SubgroupStudent], safe=True)

    if not Group.select().exists():
        g1 = Group.create(name='ИС-21')
        g2 = Group.create(name='ПО-22')

        s1 = Student.create(full_name='Иванов Иван Иванович', group=g1)
        s2 = Student.create(full_name='Петрова Мария Сергеевна', group=g1)
        s3 = Student.create(full_name='Сидоров Алексей Петрович', group=g1)
        s4 = Student.create(full_name='Кузнецова Анна Дмитриевна', group=g2)

        sg1 = Subgroup.create(name='Подгруппа 1', group=g1, purpose='Иностранный язык')
        sg2 = Subgroup.create(name='Подгруппа 2', group=g1, purpose='Иностранный язык')

        SubgroupStudent.create(subgroup=sg1, student=s1)
        SubgroupStudent.create(subgroup=sg1, student=s2)
        SubgroupStudent.create(subgroup=sg2, student=s3)


if __name__ == '__main__':
    init_db()
    print("База данных subgroup.db успешно инициализирована.")
