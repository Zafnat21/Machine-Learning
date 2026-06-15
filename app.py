import gradio as gr
import pandas as pd
import pickle

# Memuat dataset
steam_data = pd.read_csv("steam_cleaned.csv")

# Memuat model SVD
with open("steam_svd_model.pkl", "rb") as file:
    model_svd = pickle.load(file)

# Memuat model K-NN
with open("steam_knn_model.pkl", "rb") as file:
    model_knn = pickle.load(file)

# Mengambil daftar game unik
all_games = steam_data["game_title"].unique()

# Mengambil daftar user unik
all_users = steam_data["user_id"].unique()


def recommend_games(user_id, model_name):
    try:
        user_id = int(user_id)
    except:
        return "User ID harus berupa angka."

    # Mengecek apakah user ID ada di dataset
    if user_id not in all_users:
        contoh_user = ", ".join(map(str, all_users[:5]))
        return f"User ID tidak ditemukan di dataset.\n\nContoh User ID yang bisa dicoba:\n{contoh_user}"

    # Memilih model
    if model_name == "SVD":
        model = model_svd
    else:
        model = model_knn

    # Mengambil game yang sudah dimainkan user
    played_games = steam_data[steam_data["user_id"] == user_id]["game_title"].unique()

    # Mengambil game yang belum dimainkan user
    games_to_predict = [game for game in all_games if game not in played_games]

    # Membuat prediksi rating untuk setiap game
    recommendations = []

    for game in games_to_predict:
        prediction = model.predict(user_id, game)
        recommendations.append((game, prediction.est))

    # Mengurutkan hasil prediksi dari rating tertinggi
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)

    # Mengambil top 5 rekomendasi
    top_5 = recommendations[:5]

    # Menampilkan hasil
    result = f"Top 5 Rekomendasi Game untuk User ID {user_id}\n\n"

    for i, (game, score) in enumerate(top_5, start=1):
        result += f"{i}. {game} | Prediksi Rating: {score:.2f}\n"

    return result


# Tampilan aplikasi
app = gr.Interface(
    fn=recommend_games,
    inputs=[
        gr.Textbox(label="User ID Steam", placeholder="Contoh: 151603712"),
        gr.Radio(["SVD", "K-NN"], label="Pilih Model", value="SVD")
    ],
    outputs=gr.Textbox(label="Hasil Rekomendasi"),
    title="Steam Game Recommender System",
    description="Sistem rekomendasi game Steam berbasis Collaborative Filtering menggunakan model SVD dan K-NN."
)

app.launch()