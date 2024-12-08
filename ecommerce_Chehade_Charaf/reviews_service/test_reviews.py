# tests/test_reviews.py

import pytest
from models import Review
from database import db

# Existing imports and fixtures are assumed to be present above

def test_submit_review_missing_fields(client, create_token):
    """
    Test submitting a review with missing required fields.
    """
    token = create_token('user2')
    review_data = {
        # 'product_id' is missing
        'rating': 4,
        'comment': 'Missing product_id field'
    }

    response = client.post(
        '/reviews',
        headers={'Authorization': f'Bearer {token}'},
        json=review_data
    )

    assert response.status_code == 400
    data = response.get_json()
    assert 'errors' in data
    assert 'product_id' in data['errors']


def test_update_review(client, create_token, app):
    """
    Test updating an existing review.
    """
    # Create a review
    with app.app_context():
        review = Review(
            product_id=2,
            username='user4',
            rating=3,
            comment='Average product',
            is_approved=True
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    token = create_token('user4')
    updated_data = {
        'rating': 4,
        'comment': 'Updated to good product'
    }

    response = client.put(
        f'/reviews/{review_id}',
        headers={'Authorization': f'Bearer {token}'},
        json=updated_data
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review updated and pending approval'
    assert data['review']['rating'] == updated_data['rating']
    assert data['review']['comment'] == updated_data['comment']
    assert data['review']['is_approved'] is False


def test_update_review_not_owner(client, create_token, app):
    """
    Test that a user cannot update someone else's review.
    """
    # Create a review by 'user5'
    with app.app_context():
        review = Review(
            product_id=3,
            username='user5',
            rating=2,
            comment='Not good',
            is_approved=True
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    # Attempt to update the review as 'user6'
    token = create_token('user6')
    updated_data = {
        'rating': 3,
        'comment': 'Trying to update someone else\'s review'
    }

    response = client.put(
        f'/reviews/{review_id}',
        headers={'Authorization': f'Bearer {token}'},
        json=updated_data
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'


def test_delete_review_by_owner(client, create_token, app):
    """
    Test deleting a review by its owner.
    """
    # Create a review by 'user7'
    with app.app_context():
        review = Review(
            product_id=4,
            username='user7',
            rating=5,
            comment='Loved it!',
            is_approved=True
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    token = create_token('user7')

    response = client.delete(
        f'/reviews/{review_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review deleted'

    # Verify the review is deleted
    with app.app_context():
        deleted_review = Review.query.get(review_id)
        assert deleted_review is None


def test_delete_review_by_admin(client, create_token, app):
    """
    Test that an admin can delete any review.
    """
    # Create a review by 'user8'
    with app.app_context():
        review = Review(
            product_id=5,
            username='user8',
            rating=1,
            comment='Terrible product',
            is_approved=False
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    # Create an admin token
    admin_token = create_token('admin')

    response = client.delete(
        f'/reviews/{review_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review deleted'

    # Verify the review is deleted
    with app.app_context():
        deleted_review = Review.query.get(review_id)
        assert deleted_review is None


def test_delete_review_not_owner_nor_admin(client, create_token, app):
    """
    Test that a user cannot delete someone else's review if they are not an admin.
    """
    # Create a review by 'user9'
    with app.app_context():
        review = Review(
            product_id=6,
            username='user9',
            rating=4,
            comment='Good product',
            is_approved=True
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    # Attempt to delete the review as 'user10'
    token = create_token('user10')

    response = client.delete(
        f'/reviews/{review_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'


def test_get_product_reviews(client, create_token, app):
    """
    Test retrieving all approved reviews for a product.
    """
    # Create reviews for product_id=7
    with app.app_context():
        approved_review = Review(
            product_id=7,
            username='user11',
            rating=5,
            comment='Excellent!',
            is_approved=True
        )
        unapproved_review = Review(
            product_id=7,
            username='user12',
            rating=2,
            comment='Not satisfied',
            is_approved=False
        )
        db.session.add_all([approved_review, unapproved_review])
        db.session.commit()

    response = client.get('/products/7/reviews')

    assert response.status_code == 200
    data = response.get_json()
    assert 'reviews' in data
    assert len(data['reviews']) == 1
    assert data['reviews'][0]['username'] == 'user11'
    assert data['reviews'][0]['is_approved'] is True


def test_get_customer_reviews(client, create_token, app):
    """
    Test retrieving all reviews written by a specific customer.
    """
    # Create reviews by 'user13' and 'user14'
    with app.app_context():
        review1 = Review(
            product_id=8,
            username='user13',
            rating=3,
            comment='Average',
            is_approved=True
        )
        review2 = Review(
            product_id=9,
            username='user13',
            rating=4,
            comment='Good',
            is_approved=True
        )
        review3 = Review(
            product_id=10,
            username='user14',
            rating=5,
            comment='Excellent',
            is_approved=True
        )
        db.session.add_all([review1, review2, review3])
        db.session.commit()

    token = create_token('user13')

    response = client.get(
        '/customers/user13/reviews',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'reviews' in data
    assert len(data['reviews']) == 2
    for review in data['reviews']:
        assert review['username'] == 'user13'


def test_moderate_review_as_admin(client, create_token, app):
    """
    Test moderating a review as an admin.
    """
    # Create a review to approve
    with app.app_context():
        review = Review(
            product_id=11,
            username='user15',
            rating=2,
            comment='Needs improvement',
            is_approved=False
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    admin_token = create_token('admin')

    # Approve the review
    response_approve = client.post(
        f'/reviews/{review_id}/approve',
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response_approve.status_code == 200
    data_approve = response_approve.get_json()
    assert data_approve['message'] == 'Review approved'

    # Verify the review is approved
    with app.app_context():
        approved_review = Review.query.get(review_id)
        assert approved_review.is_approved is True

    # Reject the review
    response_reject = client.post(
        f'/reviews/{review_id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response_reject.status_code == 200
    data_reject = response_reject.get_json()
    assert data_reject['message'] == 'Review rejected and deleted'

    # Verify the review is deleted
    with app.app_context():
        deleted_review = Review.query.get(review_id)
        assert deleted_review is None


def test_moderate_review_as_non_admin(client, create_token, app):
    """
    Test that non-admin users cannot moderate reviews.
    """
    # Create a review to moderate
    with app.app_context():
        review = Review(
            product_id=12,
            username='user16',
            rating=1,
            comment='Bad experience',
            is_approved=False
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    # Attempt to approve the review as a non-admin user
    token = create_token('user17')

    response = client.post(
        f'/reviews/{review_id}/approve',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'

    # Attempt to reject the review as a non-admin user
    response_reject = client.post(
        f'/reviews/{review_id}/reject',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response_reject.status_code == 403
    data_reject = response_reject.get_json()
    assert data_reject['message'] == 'Admin privileges required'


def test_get_review_details(client, create_token, app):
    """
    Test retrieving the details of a specific review.
    """
    # Create a review
    with app.app_context():
        review = Review(
            product_id=13,
            username='user18',
            rating=4,
            comment='Pretty good',
            is_approved=True
        )
        db.session.add(review)
        db.session.commit()
        review_id = review.id

    token = create_token('user18')

    response = client.get(
        f'/reviews/{review_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'review' in data
    assert data['review']['id'] == review_id
    assert data['review']['product_id'] == 13
    assert data['review']['username'] == 'user18'
    assert data['review']['rating'] == 4
    assert data['review']['comment'] == 'Pretty good'
    assert data['review']['is_approved'] is True


def test_get_review_details_not_found(client, create_token):
    """
    Test handling of requests for non-existent reviews.
    """
    token = create_token('user19')
    non_existent_review_id = 9999  # Assuming this ID does not exist

    response = client.get(
        f'/reviews/{non_existent_review_id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Review not found'
