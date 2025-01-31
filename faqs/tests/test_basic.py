from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from faqs.models import SimpleQuestion

class TestSimpleQuestion(TestCase):
    def setUp(self):
        """Set up test data"""
        self.question = SimpleQuestion.objects.create(
            question="What is a test question?",
            answer="This is a test answer",
            is_active=True
        )

    def test_question_creation(self):
        """Test 1: Basic question creation and field values"""
        self.assertEqual(self.question.question, "What is a test question?")
        self.assertEqual(self.question.answer, "This is a test answer")
        self.assertTrue(self.question.is_active)
        self.assertIsNotNone(self.question.created_at)
        self.assertIsNotNone(self.question.updated_at)
        self.assertEqual(str(self.question), "What is a test question?")

    def test_question_update(self):
        """Test 2: Question update functionality"""
        # Update the question
        self.question.question = "Updated question?"
        self.question.answer = "Updated answer"
        self.question.is_active = False
        self.question.save()

        # Refresh from database
        self.question.refresh_from_db()

        # Check updated values
        self.assertEqual(self.question.question, "Updated question?")
        self.assertEqual(self.question.answer, "Updated answer")
        self.assertFalse(self.question.is_active)

    def test_question_timestamps(self):
        """Test 3: Question timestamp behavior"""
        original_updated_at = self.question.updated_at
        
        # Wait a second to ensure timestamp will be different
        import time
        time.sleep(1)
        
        # Make a change
        self.question.question = "New question"
        self.question.save()
        
        # Refresh from database
        self.question.refresh_from_db()
        
        # Check that updated_at was changed
        self.assertGreater(self.question.updated_at, original_updated_at)
        
        # Check that created_at remains unchanged
        self.assertLess(self.question.created_at, self.question.updated_at)

    def test_question_string_representation(self):
        """Test 4: Question string representation with long text"""
        # Create question with a very long question text
        long_question = "This is a very long question that should be truncated in the string representation. " * 3
        question = SimpleQuestion.objects.create(
            question=long_question,
            answer="Short answer"
        )
        
        # Check that string representation is truncated to 100 chars
        self.assertEqual(len(str(question)), 100)
        self.assertEqual(str(question), long_question[:100])

    def test_empty_fields_validation(self):
        """Test 5: Validation of empty required fields"""
        # Test empty question
        with self.assertRaises(ValidationError):
            question = SimpleQuestion(answer="Answer without question")
            question.full_clean()

        # Test empty answer
        with self.assertRaises(ValidationError):
            question = SimpleQuestion(question="Question without answer")
            question.full_clean()

    def test_bulk_creation_and_update(self):
        """Test 6: Bulk creation and update operations"""
        # Bulk create questions
        questions_to_create = [
            SimpleQuestion(question=f"Bulk Question {i}", answer=f"Bulk Answer {i}")
            for i in range(3)
        ]
        SimpleQuestion.objects.bulk_create(questions_to_create)
        
        # Verify bulk creation
        self.assertEqual(SimpleQuestion.objects.count(), 4)  # 3 new + 1 from setUp
        
        # Bulk update
        questions = SimpleQuestion.objects.all()
        for q in questions:
            q.is_active = False
        SimpleQuestion.objects.bulk_update(questions, ['is_active'])
        
        # Verify bulk update
        self.assertEqual(SimpleQuestion.objects.filter(is_active=False).count(), 4)

    def test_ordering(self):
        """Test 7: Model ordering by created_at"""
        # Delete existing questions to start fresh
        SimpleQuestion.objects.all().delete()
        
        # Create questions with different timestamps
        import time
        
        # Create first question and wait
        question1 = SimpleQuestion.objects.create(
            question="First question",
            answer="First answer"
        )
        time.sleep(0.1)  # Wait to ensure different timestamps
        
        # Create second question
        question2 = SimpleQuestion.objects.create(
            question="Second question",
            answer="Second answer"
        )
        
        # Get ordered questions
        questions = list(SimpleQuestion.objects.all())  # Convert to list to ensure order
        
        # Should only have 2 questions in reverse chronological order
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0].question, "Second question")
        self.assertEqual(questions[1].question, "First question")

    def test_filtering_and_exclusion(self):
        """Test 8: Filtering and exclusion operations"""
        # Create additional questions with varying states
        SimpleQuestion.objects.create(
            question="Active question",
            answer="Active answer",
            is_active=True
        )
        SimpleQuestion.objects.create(
            question="Inactive question",
            answer="Inactive answer",
            is_active=False
        )
        
        # Test filtering
        active_questions = SimpleQuestion.objects.filter(is_active=True)
        self.assertEqual(active_questions.count(), 2)
        
        # Test exclusion
        inactive_questions = SimpleQuestion.objects.exclude(is_active=True)
        self.assertEqual(inactive_questions.count(), 1)
        
        # Test complex query
        specific_questions = SimpleQuestion.objects.filter(
            is_active=True
        ).exclude(
            question__startswith="What"
        )
        self.assertEqual(specific_questions.count(), 1)

    def test_case_sensitivity_and_special_chars(self):
        """Test 9: Handling of case sensitivity and special characters"""
        # Test case sensitivity
        question1 = SimpleQuestion.objects.create(
            question="UPPERCASE QUESTION",
            answer="UPPERCASE ANSWER"
        )
        question2 = SimpleQuestion.objects.create(
            question="uppercase question",
            answer="uppercase answer"
        )
        
        # Verify both questions exist and are different
        case_questions = SimpleQuestion.objects.filter(
            question__in=["UPPERCASE QUESTION", "uppercase question"]
        )
        self.assertEqual(case_questions.count(), 2)
        
        # Test special characters
        special_chars = "What's this? (Special) [Characters] {Test} <Here>!"
        question3 = SimpleQuestion.objects.create(
            question=special_chars,
            answer="Answer with special chars: @#$%^&*"
        )
        
        # Verify special characters are preserved
        retrieved = SimpleQuestion.objects.get(pk=question3.pk)
        self.assertEqual(retrieved.question, special_chars)

    def test_model_methods_and_properties(self):
        """Test 10: Model methods and properties"""
        # Test string truncation with exactly 100 chars
        exact_100 = "x" * 100
        question = SimpleQuestion.objects.create(
            question=exact_100,
            answer="Test answer"
        )
        self.assertEqual(len(str(question)), 100)
        
        # Test string truncation with 99 chars
        under_100 = "y" * 99
        question = SimpleQuestion.objects.create(
            question=under_100,
            answer="Test answer"
        )
        self.assertEqual(len(str(question)), 99)
        
        # Test ordering property
        self.assertEqual(
            SimpleQuestion._meta.ordering,
            ['-created_at']
        ) 