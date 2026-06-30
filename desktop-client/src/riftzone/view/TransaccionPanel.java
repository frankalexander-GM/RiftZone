package riftzone.view;

import riftzone.dao.TransaccionDAO;
import riftzone.model.Transaccion;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class TransaccionPanel extends JPanel {
    private TransaccionDAO dao = new TransaccionDAO();
    private JTable tabla;
    private DefaultTableModel model;

    public TransaccionPanel() {
        setLayout(new BorderLayout());
        initComponents();
        cargarDatos();
    }

    private void initComponents() {
        String[] cols = {"ID", "User ID", "Amount", "Tipo", "Descripcion", "Fecha"};
        model = new DefaultTableModel(cols, 0) {
            @Override public boolean isCellEditable(int r, int c) { return false; }
        };
        tabla = new JTable(model);
        tabla.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JButton btnNuevo = new JButton("Nueva Transaccion");
        JButton btnRefrescar = new JButton("Refrescar");

        btnNuevo.addActionListener(e -> nuevaTransaccion());
        btnRefrescar.addActionListener(e -> cargarDatos());

        top.add(btnNuevo); top.add(btnRefrescar);
        add(top, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
    }

    private void cargarDatos() {
        model.setRowCount(0);
        try {
            for (Transaccion t : dao.listar()) {
                model.addRow(new Object[]{t.getId(), t.getUserId(), t.getAmount(), t.getTipo(), t.getDescription(), t.getCreatedAt()});
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error: " + e.getMessage());
        }
    }

    private void nuevaTransaccion() {
        JTextField txtUser = new JTextField("1");
        JTextField txtAmount = new JTextField("100");
        JComboBox<String> cbTipo = new JComboBox<>(new String[]{"ingreso", "egreso"});
        JTextField txtDesc = new JTextField("Compra de prueba");
        Object[] campos = {"User ID:", txtUser, "Amount:", txtAmount, "Tipo:", cbTipo, "Descripcion:", txtDesc};
        int r = JOptionPane.showConfirmDialog(this, campos, "Nueva Transaccion", JOptionPane.OK_CANCEL_OPTION);
        if (r == JOptionPane.OK_OPTION) {
            try {
                Transaccion t = new Transaccion();
                t.setUserId(Integer.parseInt(txtUser.getText()));
                t.setAmount(Integer.parseInt(txtAmount.getText()));
                t.setTipo((String) cbTipo.getSelectedItem());
                t.setDescription(txtDesc.getText());
                dao.insertar(t);
                cargarDatos();
            } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }
}
