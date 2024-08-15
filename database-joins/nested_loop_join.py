"""
Nested Loop Join
===============

Nested Loop Join is a join algorithm that works by iterating over each row in one table and comparing it with each row in the other table. If the join condition is satisfied, the rows are joined and returned as the result.

1. For each row in the left table:
	a. For each row in the right table:
		i. Check if the join condition is satisfied.
		ii. If the join condition is satisfied, join the rows and store the result in the resultset.

Time Complexity:
1. The time complexity of the Nested Loop Join algorithm is O(n * m), where n is the number of rows in the left table and m is the number of rows in the right table.

Space Complexity: O(1)

Example:
In this example, we will create two tables, `employees` and `departments`, and join them on the `department_id` column using the Nested Loop Join algorithm.
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


def nested_loop_join(
    employees: List[Employee], departments: List[Department]
) -> List[Result]:
    result = []
    for employee in employees:
        for department in departments:
            if employee.department_id == department.id:
                result.append(Result(employee.id, employee.name, department.id, department.name))
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
        Department(id=4, name="HR"),
    ]

    # Join employees and departments using Nested Loop Join
    result = nested_loop_join(employees, departments)

    # Print the result
    for record in result:
        print(record)
