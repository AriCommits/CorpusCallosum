"""Quiz generation logic."""

from typing import Optional

from corpus_callosum.db import DatabaseBackend

from .config import QuizConfig


class QuizGenerator:
    """Generate quizzes from documents in a collection."""

    def __init__(self, config: QuizConfig, db: DatabaseBackend):
        """Initialize quiz generator.

        Args:
            config: Quiz configuration
            db: Database backend
        """
        self.config = config
        self.db = db

    def generate(
        self, collection: str, count: Optional[int] = None
    ) -> list[dict[str, any]]:
        """Generate quiz questions from collection.

        Args:
            collection: Collection name
            count: Number of questions to generate (uses config default if None)

        Returns:
            List of question dicts with 'question', 'type', 'answer', 'options', 'explanation' keys
        """
        if count is None:
            count = self.config.questions_per_topic

        # Get full collection name with prefix
        full_collection = f"{self.config.collection_prefix}_{collection}"

        # Check if collection exists
        if not self.db.collection_exists(full_collection):
            raise ValueError(f"Collection '{full_collection}' does not exist")

        # For now, return placeholder questions
        # In full implementation, this would:
        # 1. Query the database for relevant documents
        # 2. Use LLM to generate quiz questions from the documents
        # 3. Distribute questions according to difficulty_distribution
        # 4. Mix question types according to question_types

        questions = []
        for i in range(count):
            # Cycle through question types
            q_type = self.config.question_types[i % len(self.config.question_types)]
            
            question_data = {
                "question": f"Question {i+1}?",
                "type": q_type,
                "collection": collection,
            }

            # Add type-specific fields
            if q_type == "multiple_choice":
                question_data["options"] = ["Option A", "Option B", "Option C", "Option D"]
                question_data["answer"] = "Option A"
            elif q_type == "true_false":
                question_data["options"] = ["True", "False"]
                question_data["answer"] = "True"
            else:  # short_answer
                question_data["answer"] = f"Answer {i+1}"

            if self.config.include_explanations:
                question_data["explanation"] = f"Explanation for question {i+1}"

            questions.append(question_data)

        return questions

    def format_quiz(self, questions: list[dict[str, any]]) -> str:
        """Format quiz questions according to config format.

        Args:
            questions: List of question dicts

        Returns:
            Formatted quiz string
        """
        if self.config.format == "markdown":
            return self._format_markdown(questions)
        elif self.config.format == "json":
            import json
            return json.dumps(questions, indent=2)
        else:  # csv
            return self._format_csv(questions)

    def _format_markdown(self, questions: list[dict[str, any]]) -> str:
        """Format as markdown."""
        lines = ["# Quiz", ""]
        
        for i, q in enumerate(questions, 1):
            lines.append(f"## Question {i}")
            lines.append(f"**{q['question']}**")
            lines.append("")
            
            if "options" in q:
                for opt in q["options"]:
                    lines.append(f"- {opt}")
                lines.append("")
            
            lines.append(f"**Answer:** {q['answer']}")
            
            if self.config.include_explanations and "explanation" in q:
                lines.append(f"**Explanation:** {q['explanation']}")
            
            lines.append("")
        
        return "\n".join(lines)

    def _format_csv(self, questions: list[dict[str, any]]) -> str:
        """Format as CSV."""
        lines = ["Question,Type,Answer,Options,Explanation"]
        
        for q in questions:
            options = "|".join(q.get("options", []))
            explanation = q.get("explanation", "")
            lines.append(f'"{q["question"]}",{q["type"]},"{q["answer"]}","{options}","{explanation}"')
        
        return "\n".join(lines)
