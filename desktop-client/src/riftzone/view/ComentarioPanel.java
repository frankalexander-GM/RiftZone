package riftzone.view;

import riftzone.dao.ComentarioDAO;
import riftzone.model.Comentario;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class ComentarioPanel extends JPanel {
    private ComentarioDAO dao = new ComentarioDAO();
    private JTable tabla;
    private DefaultTableModel model;
    private JTextField txtFiltroPub;

    public ComentarioPanel() {
        setLayout(new BorderLayout());
        initComponents();
        cargarDatos();
    }

    private void initComponents() {
        String[] cols = {"ID", "ID Publicacion", "ID Usuario", "Contenido", "Fecha"};
        model = new DefaultTableModel(cols, 0) {
            @Override public boolean isCellEditable(int r, int c) { return false; }
        };
        tabla = new JTable(model);
        tabla.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        txtFiltroPub = new JTextField(8);
        JButton btnFiltrar = new JButton("Filtrar");
        JButton btnTodos = new JButton("Todos");
        JButton btnNuevo = new JButton("Nuevo");
        JButton btnEliminar = new JButton("Eliminar");

        btnFiltrar.addActionListener(e -> cargarDatos());
        btnTodos.addActionListener(e -> { txtFiltroPub.setText(""); cargarDatos(); });
        btnNuevo.addActionListener(e -> nuevoComentario());
        btnEliminar.addActionListener(e -> eliminarComentario());

        top.add(new JLabel("ID Publicacion:")); top.add(txtFiltroPub);
        top.add(btnFiltrar); top.add(btnTodos); top.add(btnNuevo); top.add(btnEliminar);
        add(top, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
    }

    private void cargarDatos() {
        model.setRowCount(0);
        try {
            List<Comentario> lista;
            String f = txtFiltroPub.getText().trim();
            if (f.isEmpty()) lista = dao.listarPorPublicacion(0);
            else lista = dao.listarPorPublicacion(Integer.parseInt(f));
            for (Comentario c : lista) {
                String cont = c.getContenido();
                if (cont != null && cont.length() > 50) cont = cont.substring(0, 50) + "...";
                model.addRow(new Object[]{c.getIdComentario(), c.getIdPublicacion(), c.getIdUsuario(), cont, c.getFechaCreacion()});
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error: " + e.getMessage());
        }
    }

    private int obtenerId() {
        int f = tabla.getSelectedRow();
        return f >= 0 ? (int) model.getValueAt(f, 0) : -1;
    }

    private void nuevoComentario() {
        JTextField txtPub = new JTextField(), txtUser = new JTextField();
        JTextArea txtCont = new JTextArea(3, 30);
        Object[] campos = {"ID Publicacion:", txtPub, "ID Usuario:", txtUser, "Comentario:", new JScrollPane(txtCont)};
        int r = JOptionPane.showConfirmDialog(this, campos, "Nuevo Comentario", JOptionPane.OK_CANCEL_OPTION);
        if (r == JOptionPane.OK_OPTION) {
            try {
                Comentario c = new Comentario();
                c.setIdPublicacion(Integer.parseInt(txtPub.getText()));
                c.setIdUsuario(Integer.parseInt(txtUser.getText()));
                c.setContenido(txtCont.getText());
                dao.insertar(c);
                cargarDatos();
            } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }

    private void eliminarComentario() {
        int id = obtenerId();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona un comentario"); return; }
        if (JOptionPane.showConfirmDialog(this, "Eliminar comentario #" + id + "?", "Confirmar", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
            try { dao.eliminar(id); cargarDatos(); } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }
}
