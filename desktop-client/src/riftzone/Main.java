package riftzone.view;

import riftzone.model.Usuario;
import javax.swing.*;

public class Main {
    public static void main(String[] args) {
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) { /* fallback */ }

        SwingUtilities.invokeLater(() -> {
            LoginView login = new LoginView(null);
            login.setVisible(true);
            Usuario u = login.getUsuarioLogueado();
            if (u != null) {
                new MainView(u).setVisible(true);
            } else {
                System.exit(0);
            }
        });
    }
}
