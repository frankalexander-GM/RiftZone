package riftzone.view;

import riftzone.controller.LoginController;
import riftzone.model.Usuario;
import javax.swing.*;
import java.awt.*;

public class LoginView extends JDialog {
    private JTextField txtEmail;
    private JPasswordField txtPassword;
    private Usuario usuarioLogueado;

    public LoginView(JFrame parent) {
        super(parent, "RiftZone - Login", true);
        setSize(400, 280);
        setLocationRelativeTo(parent);
        setResizable(false);
        initComponents();
    }

    private void initComponents() {
        JPanel p = new JPanel(new GridBagLayout());
        p.setBackground(new Color(20, 20, 30));
        GridBagConstraints g = new GridBagConstraints();
        g.insets = new Insets(8, 12, 8, 12);
        g.fill = GridBagConstraints.HORIZONTAL;

        JLabel lblTitulo = new JLabel("RiftZone Desktop");
        lblTitulo.setFont(new Font("Arial", Font.BOLD, 22));
        lblTitulo.setForeground(new Color(59, 130, 246));
        g.gridx = 0; g.gridy = 0; g.gridwidth = 2;
        p.add(lblTitulo, g);

        g.gridwidth = 1; g.gridy = 1; g.gridx = 0;
        JLabel l1 = new JLabel("Email:");
        l1.setForeground(Color.WHITE);
        p.add(l1, g);

        g.gridx = 1;
        txtEmail = new JTextField(18);
        txtEmail.setText("frank@adm.com");
        p.add(txtEmail, g);

        g.gridy = 2; g.gridx = 0;
        JLabel l2 = new JLabel("Password:");
        l2.setForeground(Color.WHITE);
        p.add(l2, g);

        g.gridx = 1;
        txtPassword = new JPasswordField(18);
        txtPassword.setText("12345678SQ");
        p.add(txtPassword, g);

        g.gridy = 3; g.gridx = 0; g.gridwidth = 2;
        JButton btnLogin = new JButton("Iniciar Sesion");
        btnLogin.setBackground(new Color(59, 130, 246));
        btnLogin.setForeground(Color.WHITE);
        btnLogin.setFont(new Font("Arial", Font.BOLD, 14));
        btnLogin.addActionListener(e -> login());
        p.add(btnLogin, g);

        add(p);
        getRootPane().setDefaultButton(btnLogin);
    }

    private void login() {
        String email = txtEmail.getText().trim();
        String pass = new String(txtPassword.getPassword());
        try {
            LoginController ctrl = new LoginController();
            usuarioLogueado = ctrl.login(email, pass);
            if (usuarioLogueado != null) {
                dispose();
            } else {
                JOptionPane.showMessageDialog(this, "Credenciales inv\u00e1lidas", "Error", JOptionPane.ERROR_MESSAGE);
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Error de conexi\u00f3n: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public Usuario getUsuarioLogueado() { return usuarioLogueado; }
}
