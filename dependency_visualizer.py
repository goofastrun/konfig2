import os
import subprocess
import json
from pathlib import Path


class DependencyVisualizer:
    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as config_file:
            self.config = json.load(config_file)

        self.graph_visualizer_path = Path(self.config['graph_visualizer_path'])
        self.repository_path = Path(self.config['repository_path'])
        self.output_path = Path(self.config['output_path'])
        self.target_file = self.config['target_file']

    def get_commits_with_file(self):
        # Получаем все коммиты с их родителями и сообщениями
        command = [
            'git', '-C', str(self.repository_path), 'log', '--pretty=format:%H %P %s', '--all'
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            all_commits = result.stdout.strip().split('\n')

            commits_with_file = []
            for line in all_commits:
                parts = line.split(" ")
                commit_hash = parts[0]
                parents = " ".join(parts[1:-1])  # Родители
                commit_message = parts[-1]  # Сообщение коммита

                # Проверяем, что коммит затрагивает нужный файл
                show_command = [
                    'git', '-C', str(self.repository_path), 'show', '--name-only', '--pretty=format:', commit_hash
                ]
                show_result = subprocess.run(show_command, capture_output=True, text=True, check=True, encoding='utf-8')

                if self.target_file in show_result.stdout:
                    commits_with_file.append((commit_hash, parents, commit_message))

            return commits_with_file

        except subprocess.CalledProcessError as e:
            print(f"Error running git command: {e}")
            return None

    def build_graph(self, commits):
        graph = "@startuml\n"
        graph += "skinparam linetype ortho\n"
        graph += "skinparam monochrome true\n"

        # Маппим хэши на их сообщения
        commit_map = {commit[0]: commit[2] for commit in commits}
        commit_order = [commit[0] for commit in commits]  # Порядок коммитов от старых к новым

        # Строим граф с зависимостями
        for commit_hash in reversed(commit_order):  # Переворачиваем, чтобы выводить от старого к новому
            commit_message = commit_map[commit_hash]
            graph += f'"{commit_hash}" : "{commit_message}"\n'

            # Получаем родителей и строим зависимости для каждого родителя
            parents = next((parents for commit, parents, _ in commits if commit == commit_hash), None)
            if parents:
                parent_list = parents.split()  # Разделяем по пробелам, чтобы учесть несколько родителей
                for parent in parent_list:
                    graph += f'"{parent}" --> "{commit_hash}"\n'

        graph += "@enduml\n"
        return graph

    def save_graph(self, graph):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)  # Создаем директорию, если она не существует
        with open(self.output_path, 'w', encoding='utf-8') as file:
            file.write(graph)

    def display_graph(self, graph):
        print(graph)

    def run(self):
        # Получение данных о коммитах, где фигурирует целевой файл
        commits = self.get_commits_with_file()
        if commits:
            graph = self.build_graph(commits)  # Построение графа
            self.display_graph(graph)  # Вывод графа в консоль
            self.save_graph(graph)  # Сохранение графа в файл
            print(f"Graph saved to {self.output_path}")
        else:
            print("No commits found for the specified file.")


if __name__ == "__main__":
    visualizer = DependencyVisualizer('config.json')
    visualizer.run()