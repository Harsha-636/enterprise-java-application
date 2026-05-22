class LoginSystem {

    private String username = "admin";
    private String password = "admin123";

    public boolean authenticate(String user, String pass) {

        return username.equals(user) && password.equals(pass);
    }
}
