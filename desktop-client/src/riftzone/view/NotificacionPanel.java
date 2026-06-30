package riftzone.view;

import riftzone.dao.NotificacionDAO;
import riftzone.model.Notificacion;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class NotificacionPanel extends JPanel {
    private NotificacionDAO dao = new NotificacionDAO();
    private JTable tabla;
    private DefaultTableModel model;

    public NotificacionPanel() {
        setLayout(new BorderLayout());
        initComponents();
        cargarDatos();
    }

    private void initComponents() {
        String[] cols = {"ID", "Usuario ID", "Mensaje", "Tipo", "Leido", "Fecha"};
        model = new DefaultTableModel(cols, 0) {
            @Override public boolean isCellEditable(int r, int c) { return false; }
        };
        tabla = new JTable(model);
        tabla.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JButton btnNuevo = new JButton("Nueva");
        JButton btnLeer = new JButton("Marcar Leida");
        JButton btnNoLeer = new JButton("Marcar No Leida");
        JButton btnEliminar = new JButton("Eliminar");
        JButton btnRefrescar = new JButton("Refrescar");

        btnNuevo.addActionListener(e -> nuevaNotificacion());
        btnLeer.addActionListener(e -> marcarLeida(true));
        btnNoLeer.addActionListener(e -> marcarLeida(false));
        btnEliminar.addActionListener(e -> eliminarNotificacion());
        btnRefrescar.addActionListener(e -> cargarDatos());

        top.add(btnNuevo); top.add(btnLeer); top.add(btnNoLeer); top.add(btnEliminar); top.add(btnRefrescar);
        add(top, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
    }

    private void cargarDatos() {
        model.setRowCount(0);
        try {
            for (Notificacion n : dao.listar()) {
                String msg = n.getMensaje();
                if (msg != null && msg.length() > 50) msg = msg.substring(0, 50) + "...";
                model.addRow(new Object[]{n.getIdNotificacion(), n.getUsuarioId(), msg, n.getTipo(), n.isLeido() ? "SI" : "NO", n.getFechaCreacion()});
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error: " + e.getMessage());
        }
    }

    private int obtenerId() {
        int f = tabla.getSelectedRow();
        return f >= 0 ? (int) model.getValueAt(f, 0) : -1;
    }

    private void nuevaNotificacion() {
        JTextField txtUser = new JTextField("1");
        JTextField txtMsg = new JTextField(30);
        JComboBox<String> cbTipo = new JComboBox<>(new String[]{"sistema","seguidor","like","comentario","comunidad","boost"});
        Object[] campos = {"Usuario ID:", txtUser, "Mensaje:", txtMsg, "Tipo:", cbTipo};
        int r = JOptionPane.showConfirmDialog(this, campos, "Nueva Notificacion", JOptionPane.OK_CANCEL_OPTION);
        if (r == JOptionPane.OK_OPTION) {
            try {
                Notificacion n = new Notificacion();
                n.setUsuarioId(Integer.parseInt(txtUser.getText()));
                n.setMensaje(txtMsg.getText());
                n.setTipo((String) cbTipo.getSelectedItem());
                dao.insertar(n);
                cargarDatos();
            } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }

    private void marcarLeida(boolean leida) {
        int id = obtenerId();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona una notificacion"); return; }
        try { dao.marcarLeida(id, leida); cargarDatos(); } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
    }

    private void eliminarNotificacion() {
        int id = obtenerId();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona una notificacion"); return; }
        if (JOptionPane.showConfirmDialog(this, "Eliminar notificacion #" + id + "?", "Confirmar", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
            try { dao.eliminar(id); cargarDatos(); } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }
}
