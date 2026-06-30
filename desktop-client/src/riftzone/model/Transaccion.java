package riftzone.model;

public class Transaccion {
    private int id, userId, amount;
    private String tipo, description, createdAt;

    public Transaccion() {}

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }
    public int getUserId() { return userId; }
    public void setUserId(int userId) { this.userId = userId; }
    public int getAmount() { return amount; }
    public void setAmount(int amount) { this.amount = amount; }
    public String getTipo() { return tipo; }
    public void setTipo(String tipo) { this.tipo = tipo; }
    public String getDescription() { return description; }
    public void setDescription(String d) { this.description = d; }
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String d) { this.createdAt = d; }
}
