"""
Merge Join
===========

Merge Join is a join algorithm that works by first sorting the two tables to be joined on the join key. Once the tables are sorted, the join key is compared for each row in the two tables. If the join key matches, the rows are joined and returned as the result.

1. Sort the two tables to be joined on the join key.
2. Initialize two pointers, one for each table.
3. Compare the join key values:
	a. If the join key values match:
		i. join the rows
		ii. store the result in the resultset
		iii. increment the right table pointers to check for more matches (since multiple rows in the right table may have the same key).
	b. If the join key value from the left table is less than the right table, increment the left pointer.
	c. If the join key value from the right table is less than the left table, increment the right pointer.
4. Repeat this process until all rows are joined.

Time Complexity:
1. Both tables need to be sorted. Assuming n & m are the number of rows in the two tables, the sorting step takes O(n log n) and O(m log m) time.
2. The merge join step takes O(n + m) time.
3. Overall, the time complexity is O(n log n + m log m + n + m) = O(n log n + m log m).

Space Complexity: O(n+m)

Pseudocode:
1. Sort the left and right tables on the join key.
2. Initialize pointers i and j for the left and right tables.
3. While i < len(left) and j < len(right):
   a. If left[i].key == right[j].key:
      - Append the joined result to the output.
      - Increment j to process the next row in the right table.
      - If right[j].key still matches left[i].key, repeat this step.
   b. If left[i].key < right[j].key:
      - Increment i to process the next row in the left table.
   c. If right[j].key < left[i].key:
      - Increment j to process the next row in the right table.
4. Repeat until all rows are processed.


Example:
In this example, we will create two tables, `employees` and `departments`, and join them on the `department_id` column using the Merge Join algorithm.
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


def merge_join(
    employees: List[Employee], departments: List[Department]
) -> List[Result]:
    # Sort employees based on department_id
    employees.sort(key=lambda x: x.department_id)
    # Sort departments based on id
    departments.sort(key=lambda x: x.id)

    # Perform the merge operation
    result = []
    i, j = 0, 0

    while i < len(departments) and j < len(employees):
        if departments[i].id == employees[j].department_id:
            result.append(
                Result(
                    employee_id=employees[j].id,
                    employee_name=employees[j].name,
                    department_id=departments[i].id,
                    department_name=departments[i].name,
                )
            )
            j += 1
        elif departments[i].id < employees[j].department_id:
            i += 1
        else:
            j += 1
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

    # Join employees and departments using Merge Join
    result = merge_join(employees, departments)

    # Print the result
    for record in result:
        print(record)
