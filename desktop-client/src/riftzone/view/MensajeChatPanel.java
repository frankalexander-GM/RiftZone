package riftzone.view;

import riftzone.dao.MensajeChatDAO;
import riftzone.model.MensajeChat;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class MensajeChatPanel extends JPanel {
    private MensajeChatDAO dao = new MensajeChatDAO();
    private JTable tabla;
    private DefaultTableModel model;

    public MensajeChatPanel() {
        setLayout(new BorderLayout());
        initComponents();
        cargarDatos();
    }

    private void initComponents() {
        String[] cols = {"ID", "Usuario ID", "Mensaje", "Fecha"};
        model = new DefaultTableModel(cols, 0) {
            @Override public boolean isCellEditable(int r, int c) { return false; }
        };
        tabla = new JTable(model);
        tabla.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JButton btnNuevo = new JButton("Enviar Mensaje");
        JButton btnEliminar = new JButton("Eliminar");
        JButton btnRefrescar = new JButton("Refrescar");

        btnNuevo.addActionListener(e -> nuevoMensaje());
        btnEliminar.addActionListener(e -> eliminarMensaje());
        btnRefrescar.addActionListener(e -> cargarDatos());

        top.add(btnNuevo); top.add(btnEliminar); top.add(btnRefrescar);
        add(top, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
    }

    private void cargarDatos() {
        model.setRowCount(0);
        try {
            for (MensajeChat m : dao.listar()) {
                String cont = m.getContenido();
                if (cont != null && cont.length() > 60) cont = cont.substring(0, 60) + "...";
                model.addRow(new Object[]{m.getId(), m.getUsuarioId(), cont, m.getFechaEnvio()});
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error: " + e.getMessage());
        }
    }

    private int obtenerId() {
        int f = tabla.getSelectedRow();
        return f >= 0 ? (int) model.getValueAt(f, 0) : -1;
    }

    private void nuevoMensaje() {
        JTextField txtUser = new JTextField("1");
        JTextArea txtCont = new JTextArea(3, 30);
        Object[] campos = {"Usuario ID:", txtUser, "Mensaje:", new JScrollPane(txtCont)};
        int r = JOptionPane.showConfirmDialog(this, campos, "Nuevo Mensaje Chat", JOptionPane.OK_CANCEL_OPTION);
        if (r == JOptionPane.OK_OPTION) {
            try {
                MensajeChat m = new MensajeChat();
                m.setUsuarioId(Integer.parseInt(txtUser.getText()));
                m.setContenido(txtCont.getText());
                dao.insertar(m);
                cargarDatos();
            } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }

    private void eliminarMensaje() {
        int id = obtenerId();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona un mensaje"); return; }
        if (JOptionPane.showConfirmDialog(this, "Eliminar mensaje #" + id + "?", "Confirmar", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
            try { dao.eliminar(id); cargarDatos(); } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }
}
