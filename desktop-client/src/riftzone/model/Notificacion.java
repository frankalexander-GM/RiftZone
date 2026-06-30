package riftzone.model;

public class Notificacion {
    private int idNotificacion, usuarioId;
    private String mensaje, icono, enlace, tipo, fechaCreacion;
    private boolean leido;

    public Notificacion() {}

    public int getIdNotificacion() { return idNotificacion; }
    public void setIdNotificacion(int id) { this.idNotificacion = id; }
    public int getUsuarioId() { return usuarioId; }
    public void setUsuarioId(int id) { this.usuarioId = id; }
    public String getMensaje() { return mensaje; }
    public void setMensaje(String m) { this.mensaje = m; }
    public String getTipo() { return tipo; }
    public void setTipo(String t) { this.tipo = t; }
    public boolean isLeido() { return leido; }
    public void setLeido(boolean l) { this.leido = l; }
    public String getIcono() { return icono; }
    public void setIcono(String i) { this.icono = i; }
    public String getEnlace() { return enlace; }
    public void setEnlace(String e) { this.enlace = e; }
    public String getFechaCreacion() { return fechaCreacion; }
    public void setFechaCreacion(String f) { this.fechaCreacion = f; }
}
