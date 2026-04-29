<?php

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;

class Guzzler
{
    // PokéAPI is unauthenticated — no key required. The header/URL-param key
    // patterns below are kept as commented-out reminders for when you re-target
    // this client at an authenticated API.
    private $apiKey       = "abc-***-***-123";
    private $api_endpoint = "https://pokeapi.co/api/v2/";
    private $headers      = array(
        "Content-Type" => "application/json",
        // use this in case the api key goes into the header
        // "apiKey" => $this->apiKey
    );

    private $client;

    public function __construct()
    {
        $this->client = new Client();
    }

    public function GetAsync($query, $getRawContent = false)
    {
        try{
            // use this in case the api key goes into the url parameters
            // if(str_contains($query, '?')){
            //     $query = $query . '&apiKey=' . $this->apiKey;
            // } else {
            //     $query = $query . '?apiKey=' . $this->apiKey;
            // }

            $response = $this->client->request('GET', $this->api_endpoint . $query, ['headers' => $this->headers]);
            $content = $response->getBody()->getContents();
            if($getRawContent){
                // use this to return text or xml
                return $content;
            } else {
                // use this for normal json
                $result = json_decode($content);
                return $result;
            }
        } catch (GuzzleException $e){
            return $e->getMessage();
        }
    }

    public function PutAsync($query, $body = null)
    {
        try{
            $response = $this->client->request('PUT', $this->api_endpoint . $query, ['headers' => $this->headers, 'body' => json_encode($body)]);
            $content = $response->getBody()->getContents();
            $result = json_decode($content);
            return $result;
        } catch (GuzzleException $e){
            return $e->getMessage();
        }
    }

    public function DeleteAsync($query)
    {
        try{
            $response = $this->client->request('DELETE', $this->api_endpoint . $query, ['headers' => $this->headers]);
            $content = $response->getBody()->getContents();
            $result = json_decode($content);
            return $result;
        } catch (GuzzleException $e){
            return $e->getMessage();
        }
    }

    public function PostAsync($query, $body = null)
    {
        try{
            $response = $this->client->request('POST', $this->api_endpoint . $query, ['headers' => $this->headers, 'body' => json_encode($body)]);
            $content = $response->getBody()->getContents();
            $result = json_decode($content);
            return $result;
        } catch (GuzzleException $e){
            return $e->getMessage();
        }
    }

    public function PatchAsync($query, $body = null)
    {
        try{
            $response = $this->client->request('PATCH', $this->api_endpoint . $query, ['headers' => $this->headers, 'body' => json_encode($body)]);
            $content = $response->getBody()->getContents();
            $result = json_decode($content);
            return $result;
        } catch (GuzzleException $e){
            return $e->getMessage();
        }
    }
}
