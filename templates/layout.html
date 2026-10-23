<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ma Cave à Vin</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 text-gray-800 pb-20">
    <!-- Header -->
    <header class="bg-[#7D1242] text-white p-4 shadow-md sticky top-0 z-50 flex justify-between items-center">
        <h1 class="text-xl font-bold">🍷 Ma Cave à Vin</h1>
        {% if session.get('user_logged_in') %}
        <a href="{{ url_for('logout') }}" class="text-xs bg-white/20 px-2 py-1 rounded">Déco</a>
        {% endif %}
    </header>

    <!-- Messages Flash -->
    <div class="max-w-md mx-auto mt-4 px-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="p-3 mb-2 rounded-lg text-sm {% if category == 'error' %}bg-red-100 text-red-700{% else %}bg-green-100 text-green-700{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <!-- Contenu Principal -->
    <main class="max-w-md mx-auto p-4">
        {% block content %}{% endblock %}
    </main>

    <!-- Barre de Navigation Mobile en Bas (Bottom Bar) -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg flex justify-around py-3 z-50">
        <a href="{{ url_for('index') }}" class="flex flex-col items-center {% if active_tab == 'dashboard' %}text-[#7D1242] font-bold{% else %}text-gray-400{% endif %}">
            <span class="text-xl">📊</span>
            <span class="text-xs">Stats</span>
        </a>
        <a href="{{ url_for('stock') }}" class="flex flex-col items-center {% if active_tab == 'stock' %}text-[#7D1242] font-bold{% else %}text-gray-400{% endif %}">
            <span class="text-xl">🍾</span>
            <span class="text-xs">Cave</span>
        </a>
        <a href="{{ url_for('add_wine') }}" class="flex flex-col items-center {% if active_tab == 'add' %}text-[#7D1242] font-bold{% else %}text-gray-400{% endif %}">
            <span class="text-xl">➕</span>
            <span class="text-xs">Ajouter</span>
        </a>
        <a href="{{ url_for('import_export') }}" class="flex flex-col items-center {% if active_tab == 'import' %}text-[#7D1242] font-bold{% else %}text-gray-400{% endif %}">
            <span class="text-xl">📥</span>
            <span class="text-xs">Excel</span>
        </a>
        <a href="{{ url_for('settings') }}" class="flex flex-col items-center {% if active_tab == 'settings' %}text-[#7D1242] font-bold{% else %}text-gray-400{% endif %}">
            <span class="text-xl">⚙️</span>
            <span class="text-xs">Réglages</span>
        </a>
    </nav>
</body>
</html>
