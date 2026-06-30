package riftzone.model;

public class MensajeChat {
    private int id, usuarioId;
    private String contenido, fechaEnvio;

    public MensajeChat() {}

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public int getUsuarioId() { return usuarioId; }
    public void setUsuarioId(int u) { this.usuarioId = u; }
    public String getContenido() { return contenido; }
    public void setContenido(String c) { this.contenido = c; }
    public String getFechaEnvio() { return fechaEnvio; }
    public void setFechaEnvio(String f) { this.fechaEnvio = f; }
}
