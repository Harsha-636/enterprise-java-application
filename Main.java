import java.util.Scanner;

public class Main {

    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);

        LoginSystem login = new LoginSystem();

        System.out.println("===== Enterprise Java Application =====");

        System.out.print("Enter Username: ");
        String user = sc.nextLine();

        System.out.print("Enter Password: ");
        String pass = sc.nextLine();

        if (login.authenticate(user, pass)) {

            System.out.println("\nLogin Successful\n");

            EmployeeManagement management = new EmployeeManagement();

            management.addEmployee(
                new Employee(101, "Harsha", "Development", 55000)
            );

            management.addEmployee(
                new Employee(102, "Rahul", "Testing", 45000)
            );

            System.out.println("Employee Records:\n");

            management.viewEmployees();

        } else {
            System.out.println("Invalid Credentials");
        }
    }
}
