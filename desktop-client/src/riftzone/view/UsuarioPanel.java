package riftzone.view;

import riftzone.controller.UsuarioController;
import riftzone.model.Usuario;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class UsuarioPanel extends JPanel {
    private UsuarioController ctrl = new UsuarioController();
    private JTable tabla;
    private DefaultTableModel model;

    public UsuarioPanel() {
        setLayout(new BorderLayout());
        initComponents();
        cargarDatos();
    }

    private void initComponents() {
        String[] cols = {"ID", "Username", "Nombre", "Email", "Rol", "Nivel", "Tokens", "Pais"};
        model = new DefaultTableModel(cols, 0) {
            @Override public boolean isCellEditable(int r, int c) { return false; }
        };
        tabla = new JTable(model);
        tabla.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        JPanel btnPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JButton btnNuevo = new JButton("Nuevo");
        JButton btnEditar = new JButton("Editar");
        JButton btnEliminar = new JButton("Eliminar");
        JButton btnRefrescar = new JButton("Refrescar");

        btnNuevo.addActionListener(e -> nuevoUsuario());
        btnEditar.addActionListener(e -> editarUsuario());
        btnEliminar.addActionListener(e -> eliminarUsuario());
        btnRefrescar.addActionListener(e -> cargarDatos());

        btnPanel.add(btnNuevo); btnPanel.add(btnEditar); btnPanel.add(btnEliminar); btnPanel.add(btnRefrescar);
        add(btnPanel, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
    }

    private void cargarDatos() {
        model.setRowCount(0);
        try {
            for (Usuario u : ctrl.listar()) {
                model.addRow(new Object[]{u.getIdUsuario(), u.getUsername(), u.getNombre(), u.getEmail(),
                    u.getRol(), u.getNivel(), u.getTokens(), u.getPais()});
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error: " + e.getMessage());
        }
    }

    private int obtenerIdSeleccionado() {
        int fila = tabla.getSelectedRow();
        return fila >= 0 ? (int) model.getValueAt(fila, 0) : -1;
    }

    private void nuevoUsuario() {
        JTextField txtNombre = new JTextField(), txtUser = new JTextField(), txtEmail = new JTextField();
        JPasswordField txtPass = new JPasswordField();
        JComboBox<String> cbRol = new JComboBox<>(new String[]{"jugador", "admin", "streamer"});
        JTextField txtPais = new JTextField();
        Object[] campos = {"Nombre:", txtNombre, "Username:", txtUser, "Email:", txtEmail,
            "Password:", txtPass, "Rol:", cbRol, "Pais:", txtPais};
        int r = JOptionPane.showConfirmDialog(this, campos, "Nuevo Usuario", JOptionPane.OK_CANCEL_OPTION);
        if (r == JOptionPane.OK_OPTION) {
            String err = ctrl.crear(txtNombre.getText(), txtUser.getText(), txtEmail.getText(),
                new String(txtPass.getPassword()), (String) cbRol.getSelectedItem(), txtPais.getText());
            if (err != null) JOptionPane.showMessageDialog(this, err);
            else cargarDatos();
        }
    }

    private void editarUsuario() {
        int id = obtenerIdSeleccionado();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona un usuario"); return; }
        try {
            Usuario u = ctrl.obtener(id);
            if (u == null) return;
            JTextField txtNombre = new JTextField(u.getNombre());
            JTextField txtBio = new JTextField(u.getBiografia());
            JTextField txtNivel = new JTextField(String.valueOf(u.getNivel()));
            JTextField txtTokens = new JTextField(String.valueOf(u.getTokens()));
            JTextField txtPais = new JTextField(u.getPais());
            JComboBox<String> cbRol = new JComboBox<>(new String[]{"jugador", "admin", "streamer"});
            cbRol.setSelectedItem(u.getRol());
            Object[] campos = {"Nombre:", txtNombre, "Bio:", txtBio, "Nivel:", txtNivel,
                "Tokens:", txtTokens, "Pais:", txtPais, "Rol:", cbRol};
            int r = JOptionPane.showConfirmDialog(this, campos, "Editar Usuario", JOptionPane.OK_CANCEL_OPTION);
            if (r == JOptionPane.OK_OPTION) {
                String err = ctrl.actualizar(id, txtNombre.getText(), txtBio.getText(),
                    Integer.parseInt(txtNivel.getText()), Integer.parseInt(txtTokens.getText()),
                    txtPais.getText(), (String) cbRol.getSelectedItem());
                if (err != null) JOptionPane.showMessageDialog(this, err);
                else cargarDatos();
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error: " + e.getMessage());
        }
    }

    private void eliminarUsuario() {
        int id = obtenerIdSeleccionado();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona un usuario"); return; }
        int conf = JOptionPane.showConfirmDialog(this, "Eliminar usuario #" + id + "?", "Confirmar", JOptionPane.YES_NO_OPTION);
        if (conf == JOptionPane.YES_OPTION) {
            String err = ctrl.eliminar(id);
            if (err != null) JOptionPane.showMessageDialog(this, err);
            else cargarDatos();
        }
    }
}
