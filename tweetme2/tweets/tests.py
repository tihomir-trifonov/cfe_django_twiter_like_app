from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Tweet
from rest_framework.test import APIClient

# Create your tests here.

User = get_user_model()

class TweetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="TestUser" , password="!test_password#1")
        self.user_b = User.objects.create_user(username="TestUser_B" , password="!test_password#1_B")
        Tweet.objects.create(content = "1st test Tweet", user=self.user)
        Tweet.objects.create(content = "3rd test Tweet", user=self.user)
        Tweet.objects.create(content = "4th test Tweet", user=self.user_b)


    
    def test_user_created(self):
       self.assertEqual(self.user.username, "TestUser")

    def test_tweet_created(self):
        obj = Tweet.objects.create(content = "2nd test Tweet", user=self.user)
        self.assertEqual(obj.content, "2nd test Tweet")
        self.assertEqual(obj.id, 4)
        self.assertEqual(obj.user, self.user)
        self.assertEqual(self.user.username, "TestUser")

    def get_client(self):
        client = APIClient()
        client.login(username=self.user.username, password='!test_password#1')
        return client

    def get_no_client(self):
        no_client = APIClient()
        return no_client

    def test_tweet_list(self):
        client = self.get_client()
        response = client.get("/api/tweets/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()),3)
        
    def test_action_like(self):
        client = self.get_client()
        response = client.post("/api/tweets/action/", {"id":1, "action":"like"})
        self.assertEqual(response.status_code,200)
        like_count = response.json().get("likes")
        self.assertEqual(like_count,1)
        self.assertEqual(len(response.json()),5)
        
    def test_action_unlike(self):
        client = self.get_client()
        #like first
        response = client.post("/api/tweets/action/", {"id":2, "action":"like"})
        self.assertEqual(response.status_code,200)
        like_count = response.json().get("likes")
        self.assertEqual(like_count,1)
        #try unlike
        response = client.post("/api/tweets/action/", {"id":2, "action":"unlike"})
        self.assertEqual(response.status_code,200)
        like_count = response.json().get("likes")
        self.assertEqual(like_count,0)
        self.assertEqual(len(response.json()),5)

    def test_action_unlike(self):
        client = self.get_client()
        all_tweets = client.get("/api/tweets/")
        response = client.post("/api/tweets/action/", {"id":3, "action":"retweet"})
        self.assertEqual(response.status_code,201)
        all_tweets_and_retweets = client.get("/api/tweets/")
        self.assertEqual(len(all_tweets_and_retweets.json()),(len(all_tweets.json())+1))
        data = response.json()
        new_tweet_id = data.get("id")
        self.assertNotEqual(2, new_tweet_id)
        
    def test_tweet_crate_api_view(self):
        data = {"content":"new Tweet"}
        client = self.get_client()
        all_tweets = client.get("/api/tweets/")
        response = client.post("/api/tweets/create/", data)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json().get("content"), "new Tweet")
        all_tweets_and_retweets = client.get("/api/tweets/")
        self.assertEqual(len(all_tweets_and_retweets.json()),(len(all_tweets.json())+1))

    def test_tweet_detail_view(self):
        client = self.get_client()
        response = client.get("/api/tweets/1/")
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json().get("id"),1)


    def test_tweet_delete_view(self):
        client = self.get_client()
        no_client = self.get_no_client()

        response = client.delete("/api/tweets/1/delete/")
        self.assertEqual(response.status_code,200)
        response = client.delete("/api/tweets/1/delete/")
        self.assertEqual(response.status_code,404)
        response_wrong_user = client.delete("/api/tweets/3/delete/")
        self.assertEqual(response_wrong_user.status_code,403)
        response_no_user = no_client.delete("/api/tweets/3/delete/")
        self.assertEqual(response_no_user.status_code,403)
        

        # self.assertEqual(response.json().get("id"),1)





    def test_no_client_create_tweet_view(self):
        no_client = self.get_no_client()
        data = {"content":"new Tweet"}
        response_no_client = no_client.post("/api/tweets/create/", data)
        self.assertEqual(response_no_client.status_code,403)