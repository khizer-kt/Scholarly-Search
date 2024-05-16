from flask import Flask, render_template, request
import subprocess
import io
import base64
import pysolr as ps
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

app = Flask(__name__)

base_url = "http://localhost:8983/solr/projectTest"
ft1 = "http://localhost:8983/solr/projectTest/projectTest_shard1_replica_n1",
ft2 = "http://localhost:8983/solr/projectTest/projectTest_shard1_replica_n2"
solr = ps.Solr(base_url, always_commit=True)

def generate_word_cloud(titles):
    text = ' '.join(titles)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = io.BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')

    return plot_url

def store_titles(titles):
    with open('history.txt', 'a') as file:
        for title in titles:
            file.write(title + '\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    word_cloud = None
    recommendations = None

    if request.method == 'POST':
        selection = request.form['search_method']
        user_input = request.form['search_input']

        if selection == 'author':
            query = f'authors:"{user_input}"'
        elif selection == 'title':
            query = f'title:"{user_input}"'
        elif selection == 'year':
            query = f'year:"{user_input}"'
        else:
            return render_template('index.html', message="Invalid selection.")

        results = solr.search(query) 
        formatted_results = []
        titles = []
        for result in results:
            filtered_results = {key: value[0] if isinstance(value, list) else value for key, value in result.items() if key not in ['id', '_version_']}
            formatted_results.append(filtered_results)
            titles.append(filtered_results['title'])

        store_titles(titles)

        if request.form.get('get_recommendations') and user_input.strip():
            process = subprocess.Popen(['python', 'recommendations.py', user_input], stdout=subprocess.PIPE)
            output, _ = process.communicate()

            recommendations = output.decode('utf-8').strip().split('\n')

        if request.form.get('word_cloud'):
            word_cloud = generate_word_cloud(titles)

        return render_template('index.html', results=formatted_results, recommendations=recommendations, word_cloud=word_cloud)

    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
