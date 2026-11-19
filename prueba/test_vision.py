import ollama

response = ollama.chat(
    model='qwen2.5vl:7b-q8_0',
    options={
        'num_ctx':8192
    },
    messages=[
        {
            'role': 'user',
            'content': 'Describe estas pantallas',
            'images': ['Foto1.jpeg', 'Foto2.jpeg', 'Foto3.jpeg']
        }
    ]
)

print(response['message']['content'])