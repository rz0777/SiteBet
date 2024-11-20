from app import create_app

# Criação da aplicação Flask
app = create_app()

if __name__ == "__main__":
    # Rodar o servidor Flask
    app.run(debug=True)
