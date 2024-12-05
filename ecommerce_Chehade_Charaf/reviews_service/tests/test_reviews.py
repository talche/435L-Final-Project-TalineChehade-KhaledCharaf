# tests/test_reviews.py

import json
from models import Review
from database import db

def test_create_review(client, user_token):
    """Test creating a new review."""
    response = client.post(
        '/reviews',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'product_id': 1,
            'rating': 5,
            'comment': 'Great product!'
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Review submitted and pending approval'
    assert data['review']['product_id'] == 1
    assert data['review']['username'] == 'user1'
    assert data['review']['rating'] == 5
    assert data['review']['comment'] == 'Great product!'
    assert data['review']['is_approved'] is False

def test_create_review_invalid_rating(client, user_token):
    """Test creating a review with an invalid rating."""
    response = client.post(
        '/reviews',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'product_id': 1,
            'rating': 6,  # Invalid rating
            'comment': 'Invalid rating!'
        }
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'errors' in data
    assert 'rating' in data['errors']

def test_get_review_not_approved(client, user_token):
    """Test retrieving a review that is not approved."""
    # First, create a review
    review = Review(
        product_id=1,
        username='user1',
        rating=4,
        comment='Good product',
        is_approved=False
    )
    db.session.add(review)
    db.session.commit()

    response = client.get(f'/reviews/{review.id}', headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Review not approved'

def test_get_review_approved(client, admin_token, user_token):
    """Test retrieving an approved review."""
    # First, create and approve a review
    review = Review(
        product_id=1,
        username='user1',
        rating=4,
        comment='Good product',
        is_approved=True
    )
    db.session.add(review)
    db.session.commit()

    response = client.get(f'/reviews/{review.id}', headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['review']['id'] == review.id
    assert data['review']['is_approved'] is True

def test_update_review(client, user_token):
    """Test updating an existing review."""
    # Create a review
    review = Review(
        product_id=1,
        username='user1',
        rating=3,
        comment='Average product',
        is_approved=True
    )
    db.session.add(review)
    db.session.commit()

    # Update the review
    response = client.put(
        f'/reviews/{review.id}',
        headers={'Authorization': f'Bearer {user_token}'},
        json={
            'rating': 4,
            'comment': 'Updated comment'
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review updated and pending approval'
    assert data['review']['rating'] == 4
    assert data['review']['comment'] == 'Updated comment'
    assert data['review']['is_approved'] is False

def test_update_review_unauthorized(client, user_token):
    """Test updating a review by a different user."""
    # Create a review by 'user1'
    review = Review(
        product_id=1,
        username='user1',
        rating=3,
        comment='Average product',
        is_approved=True
    )
    db.session.add(review)
    db.session.commit()

    # Attempt to update the review with 'user2'
    # Generate token for 'user2'
    token = create_access_token(identity='user2')
    response = client.put(
        f'/reviews/{review.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'rating': 4,
            'comment': 'Unauthorized update'
        }
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'

def test_delete_review(client, user_token):
    """Test deleting a review."""
    # Create a review
    review = Review(
        product_id=2,
        username='user1',
        rating=2,
        comment='Not satisfied',
        is_approved=True
    )
    db.session.add(review)
    db.session.commit()

    # Delete the review
    response = client.delete(
        f'/reviews/{review.id}',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review deleted'

    # Verify deletion
    deleted_review = Review.query.get(review.id)
    assert deleted_review is None

def test_delete_review_unauthorized(client, user_token):
    """Test deleting a review by a different user."""
    # Create a review by 'user1'
    review = Review(
        product_id=2,
        username='user1',
        rating=2,
        comment='Not satisfied',
        is_approved=True
    )
    db.session.add(review)
    db.session.commit()

    # Attempt to delete the review with 'user2'
    token = create_access_token(identity='user2')
    response = client.delete(
        f'/reviews/{review.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'

def test_get_product_reviews(client, user_token):
    """Test retrieving all approved reviews for a product."""
    # Create approved and unapproved reviews
    review1 = Review(
        product_id=1,
        username='user1',
        rating=5,
        comment='Excellent!',
        is_approved=True
    )
    review2 = Review(
        product_id=1,
        username='user2',
        rating=3,
        comment='Average',
        is_approved=False
    )
    db.session.add_all([review1, review2])
    db.session.commit()

    response = client.get('/products/1/reviews')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['reviews']) == 1
    assert data['reviews'][0]['id'] == review1.id

def test_get_customer_reviews(client, user_token):
    """Test retrieving all reviews made by a customer."""
    # Create reviews by 'user1' and 'user2'
    review1 = Review(
        product_id=1,
        username='user1',
        rating=4,
        comment='Good product',
        is_approved=True
    )
    review2 = Review(
        product_id=2,
        username='user1',
        rating=2,
        comment='Not good',
        is_approved=True
    )
    review3 = Review(
        product_id=3,
        username='user2',
        rating=5,
        comment='Loved it!',
        is_approved=True
    )
    db.session.add_all([review1, review2, review3])
    db.session.commit()

    response = client.get('/customers/user1/reviews', headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['reviews']) == 2
    review_ids = [review['id'] for review in data['reviews']]
    assert review1.id in review_ids
    assert review2.id in review_ids

def test_get_customer_reviews_unauthorized(client, user_token):
    """Test retrieving reviews of another customer."""
    response = client.get('/customers/user2/reviews', headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Unauthorized access'

def test_approve_review_as_admin(client, admin_token):
    """Test approving a review as admin."""
    # Create a review
    review = Review(
        product_id=3,
        username='user1',
        rating=3,
        comment='It\'s okay',
        is_approved=False
    )
    db.session.add(review)
    db.session.commit()

    # Approve the review
    response = client.post(
        f'/reviews/{review.id}/approve',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review approved'

    # Verify approval
    updated_review = Review.query.get(review.id)
    assert updated_review.is_approved is True

def test_approve_review_as_non_admin(client, user_token):
    """Test approving a review as a non-admin user."""
    # Create a review
    review = Review(
        product_id=3,
        username='user1',
        rating=3,
        comment='It\'s okay',
        is_approved=False
    )
    db.session.add(review)
    db.session.commit()

    # Attempt to approve the review as a regular user
    response = client.post(
        f'/reviews/{review.id}/approve',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'

def test_reject_review_as_admin(client, admin_token):
    """Test rejecting a review as admin."""
    # Create a review
    review = Review(
        product_id=4,
        username='user1',
        rating=1,
        comment='Terrible product',
        is_approved=False
    )
    db.session.add(review)
    db.session.commit()

    # Reject the review
    response = client.post(
        f'/reviews/{review.id}/reject',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review rejected and deleted'

    # Verify rejection (deletion)
    deleted_review = Review.query.get(review.id)
    assert deleted_review is None

def test_reject_review_as_non_admin(client, user_token):
    """Test rejecting a review as a non-admin user."""
    # Create a review
    review = Review(
        product_id=4,
        username='user1',
        rating=1,
        comment='Terrible product',
        is_approved=False
    )
    db.session.add(review)
    db.session.commit()

    # Attempt to reject the review as a regular user
    response = client.post(
        f'/reviews/{review.id}/reject',
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'
