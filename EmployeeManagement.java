import java.util.ArrayList;

class EmployeeManagement {

    ArrayList<Employee> employees = new ArrayList<>();

    public void addEmployee(Employee emp) {
        employees.add(emp);
        System.out.println("Employee Added Successfully\n");
    }

    public void viewEmployees() {

        if (employees.isEmpty()) {
            System.out.println("No Employees Found");
            return;
        }

        for (Employee emp : employees) {
            emp.displayEmployee();
            System.out.println("-------------------");
        }
    }
}
