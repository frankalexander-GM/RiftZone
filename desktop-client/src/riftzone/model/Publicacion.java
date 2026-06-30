package riftzone.model;

public class Publicacion {
    private int idPublicacion, idUsuario;
    private String contenido, imagenUrl, videoArchivo, juego, fechaCreacion;
    private String repostId, boostTipo, boostHasta;
    private boolean promocionada, fijada;
    private int sharesCount;

    public Publicacion() {}

    public int getIdPublicacion() { return idPublicacion; }
    public void setIdPublicacion(int id) { this.idPublicacion = id; }
    public int getIdUsuario() { return idUsuario; }
    public void setIdUsuario(int id) { this.idUsuario = id; }
    public String getContenido() { return contenido; }
    public void setContenido(String c) { this.contenido = c; }
    public String getJuego() { return juego; }
    public void setJuego(String j) { this.juego = j; }
    public String getFechaCreacion() { return fechaCreacion; }
    public void setFechaCreacion(String f) { this.fechaCreacion = f; }
    public String getVideoArchivo() { return videoArchivo; }
    public void setVideoArchivo(String v) { this.videoArchivo = v; }
    public String getBoostTipo() { return boostTipo; }
    public void setBoostTipo(String b) { this.boostTipo = b; }
    public String getBoostHasta() { return boostHasta; }
    public void setBoostHasta(String b) { this.boostHasta = b; }
    public boolean isPromocionada() { return promocionada; }
    public void setPromocionada(boolean p) { this.promocionada = p; }
    public boolean isFijada() { return fijada; }
    public void setFijada(boolean f) { this.fijada = f; }
    public int getSharesCount() { return sharesCount; }
    public void setSharesCount(int s) { this.sharesCount = s; }
    public String getImagenUrl() { return imagenUrl; }
    public void setImagenUrl(String i) { this.imagenUrl = i; }

    @Override public String toString() { return "#" + idPublicacion + " - " + (contenido != null && contenido.length() > 40 ? contenido.substring(0, 40) : contenido); }
}
