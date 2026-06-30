package riftzone.model;

public class Comentario {
    private int idComentario, idPublicacion, idUsuario;
    private String contenido, fechaCreacion;

    public Comentario() {}

    public int getIdComentario() { return idComentario; }
    public void setIdComentario(int id) { this.idComentario = id; }
    public int getIdPublicacion() { return idPublicacion; }
    public void setIdPublicacion(int id) { this.idPublicacion = id; }
    public int getIdUsuario() { return idUsuario; }
    public void setIdUsuario(int id) { this.idUsuario = id; }
    public String getContenido() { return contenido; }
    public void setContenido(String c) { this.contenido = c; }
    public String getFechaCreacion() { return fechaCreacion; }
    public void setFechaCreacion(String f) { this.fechaCreacion = f; }
}
