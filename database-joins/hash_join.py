"""
Hash Join
=========

A Hash Join is an efficient algorithm used to perform join operations in relational databases. It is particularly useful when joining large datasets and is often faster than nested loop joins or merge joins, especially when the datasets are not sorted. 
The basic idea behind a hash join is to use a hash table to partition the smaller of the two tables (referred to as the "build" table), and then probe the hash table with the larger table (referred to as the "probe" table) to find matching rows.

Algorithm:
1. Build a hash table from the smaller of the two tables based on the join key.
2. Iterate over the larger table and probe the hash table to find matching rows.
3. For each matching row, combine the rows from both tables to form the result.


Time Complexity:
1. Building the hash table takes O(n) time, where n is the number of rows in the smaller table.
2. Probing the hash table takes O(m) time, where m is the number of rows in the larger table.
3. Overall, the time complexity is O(n + m).

Space Complexity: O(n)

Additional Notes:
1. This is well suited for "equi-joins" where the join condition is based on equality. Ex - `employees.department_id = departments.id`.
2. Hash table requires additional memory, so it may not be suitable for very large datasets that do not fit in memory.

Example:
In this example, we will create two tables, `employees` and `departments`, and join them on the `department_id` column using the Hash Join algorithm.
"""

from typing import List
from dataclasses import dataclass


@dataclass
class Employee:
    id: int
    name: str
    department_id: int


@dataclass
class Department:
    id: int
    name: str


@dataclass
class Result:
    employee_id: int
    employee_name: str
    department_id: int
    department_name: str

    def __repr__(self) -> str:
        return f"Employee ID: {self.employee_id}, Employee Name: {self.employee_name}, Department ID: {self.department_id}, Department Name: {self.department_name}"


def hash_join(employees: List[Employee], departments: List[Department]) -> List[Result]:
    result = []

    # Build a hash table from the smaller of the two tables (departments)
    # The hash table will store the department_id as the key and the corresponding department name as the value
    department_hash = {department.id: department.name for department in departments}

    # Iterate over the larger table (employees) and probe the hash table to find matching rows
    # TODO: Need to check how this would work when joining 2 tables which have multiple matching rows
    for employee in employees:
        department_name = department_hash.get(employee.department_id)
        if department_name:
            result.append(
                Result(
                    employee.id, employee.name, employee.department_id, department_name
                )
            )

    return result


if __name__ == "__main__":
    # Create sample data for employees and departments
    employees = [
        Employee(id=1, name="Alice", department_id=1),
        Employee(id=2, name="Bob", department_id=2),
        Employee(id=3, name="Charlie", department_id=1),
        Employee(id=4, name="David", department_id=3),
    ]

    departments = [
        Department(id=1, name="Engineering"),
        Department(id=2, name="Sales"),
        Department(id=3, name="Marketing"),
        Department(id=4, name="Operations"),
    ]

    # Join employees and departments using Hash Join
    result = hash_join(employees, departments)

    # Print the result
    for record in result:
        print(record)
