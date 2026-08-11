from app import create_app

app = create_app()

if __name__ == '__main__':
    # Running in debug mode for easy development
    app.run(debug=True, host='0.0.0.0', port=5000)
