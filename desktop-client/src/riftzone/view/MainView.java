package riftzone.view;

import riftzone.controller.DashboardController;
import riftzone.model.Usuario;
import javax.swing.*;
import java.awt.*;
import java.util.Map;

public class MainView extends JFrame {
    private Usuario usuario;
    private DashboardController dashboardCtrl = new DashboardController();

    public MainView(Usuario usuario) {
        super("RiftZone Desktop - " + usuario.getUsername());
        this.usuario = usuario;
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1100, 700);
        setLocationRelativeTo(null);
        initComponents();
    }

    private void initComponents() {
        JTabbedPane tabs = new JTabbedPane();
        tabs.addTab("Dashboard", crearPanelDashboard());
        tabs.addTab("Usuarios", new UsuarioPanel());
        tabs.addTab("Publicaciones", new PublicacionPanel());
        tabs.addTab("Comentarios", new ComentarioPanel());
        tabs.addTab("Transacciones", new TransaccionPanel());
        tabs.addTab("Notificaciones", new NotificacionPanel());
        tabs.addTab("Chat Global", new MensajeChatPanel());
        add(tabs);
    }

    private JPanel crearPanelDashboard() {
        JPanel p = new JPanel(new GridLayout(0, 4, 10, 10));
        p.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        Map<String, Object> stats = dashboardCtrl.getEstadisticas();
        String[] labels = {
            "usuarios", "Usuarios", "publicaciones", "Publicaciones",
            "comentarios", "Comentarios", "transacciones", "Transacciones",
            "notificaciones", "Notificaciones", "mensajes_chat", "Chat",
            "seguidores", "Seguidores", "comunidades_seguidas", "Comunidades"
        };
        Color[] colors = {
            new Color(59,130,246), new Color(168,85,247), new Color(34,197,94), new Color(251,191,36),
            new Color(239,68,68), new Color(236,72,153), new Color(20,184,166), new Color(249,115,22)
        };
        for (int i = 0; i < labels.length; i += 2) {
            Object val = stats.getOrDefault(labels[i], 0);
            p.add(crearCard(labels[i+1], String.valueOf(val), colors[i/2]));
        }
        JPanel wrapper = new JPanel(new BorderLayout());
        JLabel bienvenida = new JLabel("Bienvenido, " + usuario.getNombre() + " (" + usuario.getRol() + ")", SwingConstants.CENTER);
        bienvenida.setFont(new Font("Arial", Font.BOLD, 18));
        wrapper.add(bienvenida, BorderLayout.NORTH);
        wrapper.add(new JScrollPane(p), BorderLayout.CENTER);
        return wrapper;
    }

    private JPanel crearCard(String titulo, String valor, Color color) {
        JPanel card = new JPanel(new BorderLayout());
        card.setBackground(new Color(30, 30, 45));
        card.setBorder(BorderFactory.createLineBorder(color.darker(), 2));
        JLabel lblValor = new JLabel(valor, SwingConstants.CENTER);
        lblValor.setFont(new Font("Arial", Font.BOLD, 36));
        lblValor.setForeground(color);
        JLabel lblTit = new JLabel(titulo, SwingConstants.CENTER);
        lblTit.setForeground(Color.LIGHT_GRAY);
        card.add(lblValor, BorderLayout.CENTER);
        card.add(lblTit, BorderLayout.SOUTH);
        return card;
    }
}
