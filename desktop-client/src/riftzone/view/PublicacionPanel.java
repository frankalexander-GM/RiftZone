package riftzone.view;

import riftzone.dao.PublicacionDAO;
import riftzone.model.Publicacion;
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class PublicacionPanel extends JPanel {
    private PublicacionDAO dao = new PublicacionDAO();
    private JTable tabla;
    private DefaultTableModel model;
    private JComboBox<String> cbFiltro;

    public PublicacionPanel() {
        setLayout(new BorderLayout());
        initComponents();
        cargarDatos();
    }

    private void initComponents() {
        String[] cols = {"ID", "ID Usuario", "Contenido", "Juego", "Promocionada", "Fecha"};
        model = new DefaultTableModel(cols, 0) {
            @Override public boolean isCellEditable(int r, int c) { return false; }
        };
        tabla = new JTable(model);
        tabla.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        cbFiltro = new JComboBox<>();
        cbFiltro.addItem("Todas");
        cbFiltro.addItem("Valorant"); cbFiltro.addItem("Minecraft"); cbFiltro.addItem("League of Legends");
        cbFiltro.addItem("Rocket League"); cbFiltro.addItem("Fortnite"); cbFiltro.addItem("Apex Legends");
        cbFiltro.addItem("Counter-Strike 2");
        cbFiltro.addActionListener(e -> cargarDatos());

        JButton btnNuevo = new JButton("Nuevo");
        JButton btnEditar = new JButton("Editar");
        JButton btnEliminar = new JButton("Eliminar");
        JButton btnRefrescar = new JButton("Refrescar");

        btnNuevo.addActionListener(e -> nuevaPublicacion());
        btnEditar.addActionListener(e -> editarPublicacion());
        btnEliminar.addActionListener(e -> eliminarPublicacion());
        btnRefrescar.addActionListener(e -> cargarDatos());

        top.add(new JLabel("Filtro: ")); top.add(cbFiltro);
        top.add(btnNuevo); top.add(btnEditar); top.add(btnEliminar); top.add(btnRefrescar);
        add(top, BorderLayout.NORTH);
        add(new JScrollPane(tabla), BorderLayout.CENTER);
    }

    private void cargarDatos() {
        model.setRowCount(0);
        try {
            String juego = (String) cbFiltro.getSelectedItem();
            List<Publicacion> lista = "Todas".equals(juego) ? dao.listar() : dao.listar(juego);
            for (Publicacion p : lista) {
                String cont = p.getContenido();
                if (cont != null && cont.length() > 50) cont = cont.substring(0, 50) + "...";
                model.addRow(new Object[]{p.getIdPublicacion(), p.getIdUsuario(), cont,
                    p.getJuego(), p.isPromocionada() ? "SI" : "NO", p.getFechaCreacion()});
            }
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error: " + e.getMessage());
        }
    }

    private int obtenerId() {
        int f = tabla.getSelectedRow();
        return f >= 0 ? (int) model.getValueAt(f, 0) : -1;
    }

    private void nuevaPublicacion() {
        JTextField txtUserId = new JTextField("1");
        JTextArea txtCont = new JTextArea(3, 30);
        JComboBox<String> cbJuego = new JComboBox<>(new String[]{"Valorant","Minecraft","League of Legends","Rocket League","Fortnite","Apex Legends","Counter-Strike 2"});
        Object[] campos = {"ID Usuario:", txtUserId, "Contenido:", new JScrollPane(txtCont), "Juego:", cbJuego};
        int r = JOptionPane.showConfirmDialog(this, campos, "Nueva Publicacion", JOptionPane.OK_CANCEL_OPTION);
        if (r == JOptionPane.OK_OPTION) {
            try {
                Publicacion p = new Publicacion();
                p.setIdUsuario(Integer.parseInt(txtUserId.getText()));
                p.setContenido(txtCont.getText());
                p.setJuego((String) cbJuego.getSelectedItem());
                dao.insertar(p);
                cargarDatos();
            } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }

    private void editarPublicacion() {
        int id = obtenerId();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona una publicacion"); return; }
        try {
            Publicacion p = dao.obtener(id);
            if (p == null) return;
            JTextArea txtCont = new JTextArea(p.getContenido(), 3, 30);
            JComboBox<String> cbJuego = new JComboBox<>(new String[]{"Valorant","Minecraft","League of Legends","Rocket League","Fortnite","Apex Legends","Counter-Strike 2"});
            cbJuego.setSelectedItem(p.getJuego());
            JCheckBox chkPromo = new JCheckBox("Promocionada", p.isPromocionada());
            Object[] campos = {"Contenido:", new JScrollPane(txtCont), "Juego:", cbJuego, "", chkPromo};
            int r = JOptionPane.showConfirmDialog(this, campos, "Editar Publicacion #" + id, JOptionPane.OK_CANCEL_OPTION);
            if (r == JOptionPane.OK_OPTION) {
                p.setContenido(txtCont.getText());
                p.setJuego((String) cbJuego.getSelectedItem());
                p.setPromocionada(chkPromo.isSelected());
                dao.actualizar(p);
                cargarDatos();
            }
        } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
    }

    private void eliminarPublicacion() {
        int id = obtenerId();
        if (id < 0) { JOptionPane.showMessageDialog(this, "Selecciona una publicacion"); return; }
        if (JOptionPane.showConfirmDialog(this, "Eliminar publicacion #" + id + "?", "Confirmar", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
            try { dao.eliminar(id); cargarDatos(); } catch (Exception e) { JOptionPane.showMessageDialog(this, "Error: " + e.getMessage()); }
        }
    }
}
