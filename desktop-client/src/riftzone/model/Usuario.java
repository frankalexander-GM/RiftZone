package riftzone.model;

public class Usuario {
    private int idUsuario;
    private String nombre, username, email, password, rol, biografia, fotoPerfil, banner;
    private int nivel, xp, xpMax, tokens;
    private String estado, fechaRegistro, juegosFavoritos, pais, disponibilidad, plataformas;
    private String estadoPersonalizado, twitch, kick, youtube, discord, steam, tituloPerfil;
    private String membresiaTipo, marcoPerfil;
    private boolean esPremium;
    private int chatUltimoVisto;

    public Usuario() {}

    public int getIdUsuario() { return idUsuario; }
    public void setIdUsuario(int idUsuario) { this.idUsuario = idUsuario; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getRol() { return rol; }
    public void setRol(String rol) { this.rol = rol; }
    public String getBiografia() { return biografia; }
    public void setBiografia(String biografia) { this.biografia = biografia; }
    public int getNivel() { return nivel; }
    public void setNivel(int nivel) { this.nivel = nivel; }
    public int getXp() { return xp; }
    public void setXp(int xp) { this.xp = xp; }
    public int getTokens() { return tokens; }
    public void setTokens(int tokens) { this.tokens = tokens; }
    public String getPais() { return pais; }
    public void setPais(String pais) { this.pais = pais; }
    public String getFechaRegistro() { return fechaRegistro; }
    public void setFechaRegistro(String fechaRegistro) { this.fechaRegistro = fechaRegistro; }

    @Override public String toString() { return username + " (" + nombre + ")"; }
}
