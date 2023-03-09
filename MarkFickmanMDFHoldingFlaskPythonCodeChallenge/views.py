{% extends 'base_onlinecourse.html' %}

{% block content %}
 <div class="container-fluid">
    {% if grade > 80 %}
        <div class="alert alert-success">
            <h5><b>Congratulations, {{user.first_name}}!</b> You have passed the exam and completed the course with score {{ grade }} / 100</h5>
        </div>
    {% else %}
        <div class="alert alert-danger">
            <h5><b>Failed</b> Sorry, {{ user.first_name }}! You have failed the exam with a score of {{ grade }} / 100</h5 class="fw-bolder">
        </div>
        <a class="btn btn-link text-danger" href="{% url 'onlinecourse:course_details' course.id %}">Re-test</a>
    {% endif %}
        <div class="card-columns-vertical mt-1">
            <h5 class="">Exam results</h5>
             {% for question in course.question_set.all %}
                <div class="card mt-1">
                    <div class="card-header"><h5>{{question.question_text}}</h5></div>
                    <div class="form-group m-2">
                        {% for choice in question.choice_set.all %}
                        <div class="form-check">
                            <!-- Format the text based on if it is true/not and if it was selected/not -->
                            {% if choice.is_correct %}
                                {% if choice.id in selections %}
                                    <label class="form-check-label text-success">Correct answer: {{choice.choice_text}}</label>
                                {% else %}
                                    <label class="form-check-label text-warning">Not selected: {{choice.choice_text}}</label>
                                {% endif %}
                            {% else %}
                                {% if choice.id in selections %}
                                    <label class="form-check-label text-danger">Wrong answer: {{choice.choice_text}}</label>
                                {% else %}
                                    <label class="form-check-label">{{choice.choice_text}}</label>
                                {% endif %}
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
            {% endfor %}
        </div>
 </div>
{% endblock %}
