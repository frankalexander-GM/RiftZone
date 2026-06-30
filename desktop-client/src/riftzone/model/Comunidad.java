package riftzone.model;

public class Comunidad {
    private String nombre, categoria, descripcion, imagen;
    private int posts, seguidores;

    public Comunidad() {}

    public String getNombre() { return nombre; }
    public void setNombre(String n) { this.nombre = n; }
    public String getCategoria() { return categoria; }
    public void setCategoria(String c) { this.categoria = c; }
    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String d) { this.descripcion = d; }
    public int getPosts() { return posts; }
    public void setPosts(int p) { this.posts = p; }
    public int getSeguidores() { return seguidores; }
    public void setSeguidores(int s) { this.seguidores = s; }
}
