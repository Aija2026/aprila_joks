import streamlit as st
import random
import time
import os
import asyncio
import tempfile
import edge_tts

# =====================
# 1. Konfigurācija un Stils
# =====================
st.set_page_config(page_title="BDA 1. aprīļa asistente", page_icon="🤡", layout="centered")

st.markdown("""
<style>
/* 1. Kustīgais fons */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #FFDEE9, #B5FFFC, #ffffff, #f0f2f6);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* 2. Čata burbuļi */
[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 20px !important;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.05) !important;
    margin-bottom: 10px !important;
}

/* 3. ATJAUNOTS: Skaistie krāsainie burti (Gradients) */
/* Selektori ir uzlaboti, lai strādātu ar jaunāko Streamlit versiju */
[data-testid="stChatMessage"] p, .stMarkdown p, [data-testid="stChatMessage"] span {
    font-size: 1.3rem !important;
    font-weight: 900 !important;
    background: linear-gradient(to right, #D4145A, #FBB03B, #00A8E8, #D4145A);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
}

@keyframes shine {
    to { background-position: 200% center; }
}

/* 4. LIELĀ SPRĀDZIENA POGA */
div.stButton > button {
    position: fixed;
    bottom: 110px;     /* Novietota virs čata ievades */
    right: 50px;       /* Atvirzīta no malas */
    width: 220px !important;
    height: 220px !important;
    background-color: #28a745 !important;
    color: white !important;
    font-size: 1.1rem !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    border: 3px solid white !important;
    /* Word Explosion formas clip-path */
    clip-path: polygon(50% 0%, 64% 18%, 88% 10%, 82% 36%, 100% 50%, 82% 64%, 88% 90%, 64% 82%, 50% 100%, 36% 82%, 12% 90%, 18% 64%, 0% 50%, 18% 36%, 12% 10%, 36% 18%);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    z-index: 1001;
    box-shadow: 0px 10px 20px rgba(0,0,0,0.3) !important;
}

div.stButton > button:hover {
    transform: scale(1.1) rotate(10deg);
    background-color: #ff4b4b !important; /* Maina krāsu uz hover */
}
</style>
""", unsafe_allow_html=True)

# =====================
# 2. Uzlabota Atbilžu Loģika
# =====================
def asistente_atbild(lietotaja_teksts):
    teksts = lietotaja_teksts.lower()
    
    # 1. Atpazīstam atslēgvārdus (arī Tavus pielāgotos)
    ir_python = "python" in teksts or "paiton" in teksts
    ir_sql = "sql" in teksts
    ir_excel = "excel" in teksts

    # 2. KOMBO loģika
    if ir_python and ir_excel:
        return "Kamēr Paiton saldi guļ, Exceli beidzot rīko kārtīgu ballīti un priecājas! 🎉"
    
    if ir_python and ir_sql and ir_excel:
        return "Paiton, SQL un Excel vienā teikumā? Tu laikam gribi uzspridzināt manu mākslīgo intelektu!"
    
    if ir_python and ir_sql:
        return "Paiton un SQL savienojums ir jaudīgs, bet šodien pat kodi atsakās komunicēt. Varbūt kafiju?"

    # 3. Atsevišķie gadījumi
    if ir_sql:
        return "SQL vaicājums atgrieza... ļoti interesantu kļūdu un vienu pazudušu tabulu."
    if ir_python:
        return "Paiton šodien importēja bibliotēku 'atpūta', un kods atteicās strādāt. Viņš tagad guļ. 😴"
    if ir_excel:
        return "Excel konstatēja, ka tavi dati ir pārāk krāsaini, un devās pensijā."
    
    # 4. Vispārīgās atbildes (Tavs pilnais saraksts)
    atbildes = [
        "Brīdinājums... pārāk augsts humora līmenis datos.",
        "Datu modelis pieprasīja... vairāk kūkas apmācības procesā.",
        "AI modelis prognozē, ka kafijas patēriņš pieaugs par 200 procentiem.",
        "Kļūda 404: Nopietnais garastāvoklis nav atrasts.",
        "Analīze pabeigta. Rezultāts: Jums steidzami nepieciešama kafija un kūka!",
        "Statistiskā ticamība liecina, ka šodien viss būs nedaudz absurds.",
        "Sistēmas paziņojums: Excel slepeni apgūst Python, lai tevi pārsteigtu.",
        "Neironu tīkls konstatēja, ka šis ir joks, un sāka smieties binārajā kodā.",
        "Datu kvalitātes pārbaude uzrādīja... pārāk daudz nopietnības.",
        "Algoritms mēģināja optimizēt dienu... bet izvēlējās pārtraukumu.",
        "Mašīnmācīšanās modelis nolēma... šodien neko nemācīties.",
        "Analītikas nodaļa nolēma... šodien analizēt jokus."
    ]
    
    if "last_response" not in st.session_state:
        st.session_state.last_response = ""
    
    izveleta = random.choice(atbildes)
    while izveleta == st.session_state.last_response:
        izveleta = random.choice(atbildes)
    
    st.session_state.last_response = izveleta
    return izveleta

async def generate_audio(text):
    voices = ["lv-LV-EveritaNeural", "lv-LV-NilsNeural"]
    voice = random.choice(voices)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(fp.name)
        return fp.name

# =====================
# 3. UI Izpilde
# =====================

st.title("🤡 BDA MI SKOLAS ASISTENTE")

if "started" not in st.session_state:
    if os.path.exists("kuratore.mp3"):
        st.audio("kuratore.mp3", format="audio/mp3", autoplay=True)
    st.session_state.started = True

try:
    st.image("asistents.jpg", width=400)
except:
    st.warning("Nav atrasts asistents.jpg")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Uzdod jautājumu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🎭"):
        atbilde = asistente_atbild(prompt)
        audio_file = asyncio.run(generate_audio(atbilde))
        st.audio(audio_file, format="audio/mp3", autoplay=True)
        
        res_box = st.empty()
        full_res = ""
        for chunk in atbilde.split():
            full_res += chunk + " "
            res_box.markdown(f"**{full_res}** ▌")
            time.sleep(0.06)
        res_box.markdown(full_res)
    st.session_state.messages.append({"role": "assistant", "content": atbilde})

# =====================
# 4. Pabeigšanas poga (Ar unikālu key)
# =====================
if st.button("🚀 PABEIGT DARBU UN DOTIES BRĪVDIENĀS", key="final_exit_btn"):
    st.balloons()
    st.success("APSVEICAM! Visi dati ir veiksmīgi sabojāti... t.i., analizēti! Varat doties atpūsties!")
    
    if os.path.exists("kuratore.mp3"):
        st.audio("kuratore.mp3", format="audio/mp3", autoplay=True)
        
    st.snow()
    time.sleep(2)
    st.warning("P.S. Šī poga neizslēdz datoru, bet gan ieslēdz 1. aprīļa režīmu! ✨")

st.caption("Izstrādāts ar Python, Streamlit un nedaudz pārāk daudz pirmā aprīļa.")