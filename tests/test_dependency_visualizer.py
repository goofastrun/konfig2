from io import StringIO
import unittest
import os
from pathlib import Path
import sys
from dependency_visualizer import DependencyVisualizer


class TestDependencyVisualizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Задаем фиктивный путь к конфигурации, который не будет использоваться
        cls.config_path = '../config.json'
        cls.visualizer = DependencyVisualizer(cls.config_path)

    def test_load_config(self):
        """Тестируем загрузку конфигурации"""
        # Проверяем, что параметры загружены корректно
        self.visualizer.load_config()
        self.assertEqual(str(self.visualizer.graph_visualizer_path),
                         "C:\\Program Files\\plantuml\\plantuml-mit-1.2024.7.jar")
        self.assertEqual(str(self.visualizer.repository_path),
                         "C:\\Users\\Станислав\\Desktop\\dependency_visualizer_project\\my_repository")
        self.assertEqual(str(self.visualizer.output_path),
                         "C:\\Users\\Станислав\\Desktop\\dependency_visualizer_project\\output.puml")
        self.assertEqual(self.visualizer.target_file, "example.py")

    def test_get_commits_with_file(self):
        """Тестируем получение коммитов, затрагивающих файл"""
        commits = self.visualizer.get_commits_with_file()
        # Проверка, что метод возвращает список коммитов
        self.assertIsNotNone(commits)
        self.assertIsInstance(commits, list)

    def test_build_graph(self):
        """Тестируем построение графа на основе фиктивных коммитов"""
        test_commits = [
            ("hashA", "", "Message A"),
            ("hashB", "hashA", "Message B"),
            ("hashC", "hashA", "Message C"),
            ("hashMerge", "hashB hashC", "Merge Message")  # Коммит merge с двумя родителями
        ]

        graph = self.visualizer.build_graph(test_commits)

        # Проверка структуры графа
        self.assertIn("@startuml", graph)
        self.assertIn("@enduml", graph)
        self.assertIn('"hashA" : "Message A"', graph)
        self.assertIn('"hashB" : "Message B"', graph)
        self.assertIn('"hashC" : "Message C"', graph)
        self.assertIn('"hashMerge" : "Merge Message"', graph)

        # Проверка зависимостей
        self.assertIn('"hashA" --> "hashB"', graph)
        self.assertIn('"hashA" --> "hashC"', graph)
        self.assertIn('"hashB" --> "hashMerge"', graph)
        self.assertIn('"hashC" --> "hashMerge"', graph)

    def test_save_graph(self):
        """Тестируем сохранение графа в файл"""
        test_commits = [
            ("hashA", "", "Message A"),
            ("hashB", "hashA", "Message B"),
            ("hashC", "hashA", "Message C"),
            ("hashMerge", "hashB hashC", "Merge Message")
        ]

        graph = self.visualizer.build_graph(test_commits)

        temp_output_path = Path("test_output.puml")
        self.visualizer.output_path = temp_output_path

        self.visualizer.save_graph(graph)
        self.assertTrue(temp_output_path.exists(), "Output file should be created")

        os.remove(temp_output_path)

    def test_display_graph(self):
        """Тестируем вывод графа на экран"""
        test_commits = [
            ("hashA", "", "Message A"),
            ("hashB", "hashA", "Message B"),
            ("hashC", "hashA", "Message C"),
            ("hashMerge", "hashB hashC", "Merge Message")
        ]

        graph = self.visualizer.build_graph(test_commits)

        # Перехватываем вывод графа
        captured_output = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured_output

        try:
            self.visualizer.display_graph(graph)
        finally:
            sys.stdout = original_stdout

        output = captured_output.getvalue()
        # Проверка, что вывод содержит идентификаторы и зависимости
        self.assertIn("hashA", output)
        self.assertIn("hashB", output)
        self.assertIn("hashC", output)
        self.assertIn("hashMerge", output)
        self.assertIn('"hashB" --> "hashMerge"', output)
        self.assertIn('"hashC" --> "hashMerge"', output)

    def test_run(self):
        """Проверяем выполнение основного метода run без ошибок"""
        try:
            self.visualizer.run()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Method run() raised an exception unexpectedly: {e}")


if __name__ == '__main__':
    unittest.main()
