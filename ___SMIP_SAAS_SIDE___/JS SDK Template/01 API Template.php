<?php

//Purpose: this script serves as an api that can ...

require_once 'thinkiq_context.php';
$context = new Context();

TiqUtilities\Model\Script::includeScript('api_demo_take_4.guzzle_client');

use Joomla\CMS\Response\JsonResponse; // Used for returning data to the client.
if (!defined('JPATH_BASE')) define('JPATH_BASE', dirname(__DIR__));

$f = isset($context->std_inputs->method) ? $context->std_inputs->method : '';
$a = isset($context->std_inputs->data)   ? json_decode($context->std_inputs->data) : '';

use TiqUtilities\GraphQL\GraphQL;

// Remote REST access — uses the Guzzler client to hit PokéAPI (unauthenticated).
// PHP-side because, in general, a browser-side fetch to a third-party host gets
// blocked by CORS. Server-to-server HTTP isn't subject to CORS, so PHP is the
// safe path for outbound REST. (PokéAPI itself happens to be CORS-permissive,
// but you can't assume that for any given third-party API.)
function GetPokemon($nameOrId){
    $client   = new Guzzler();
    $response = $client->GetAsync("pokemon/$nameOrId");
    return $response;
}

// GraphQL access from PHP — uses TiqUtilities\GraphQL\GraphQL to talk to the
// SMIP's own PostGraphile endpoint. Server-side counterpart of the JS-only
// GraphQL tool: same query, same shape; the round-trip happens in PHP rather
// than in the browser. Useful when the caller is itself a server-side script
// (cron, integration job, …) that has no browser to do GraphQL from.
//
// Case-insensitive substring search on displayName. Returns every library
// whose displayName lowercase contains the search string lowercase.
function SearchLibraryByNameViaPhp($search){
    $aClient   = new GraphQL();
    $escaped   = json_encode($search);   // safely quotes/escapes for a GraphQL string literal
    $gqlQuery  = "
        query SearchLibraryByName {
            libraries(filter: { displayName: { includesInsensitive: $escaped } }) {
                id
                displayName
            }
        }
    ";
    $response = $aClient->MakeRequest($gqlQuery);
    // PostGraphile returns an array under data.libraries; pass the whole list through.
    return isset($response->data->libraries) ? $response->data->libraries : [];
}

// Note: each tool that has a doublet ("…ViaPhp" + JS twin) is paired up with a
// browser-side counterpart in api_demo_take_4.api_tools (via:"graphql" or via:"js").
// GetPokemon is intentionally NOT doubled — the JS path would (in general)
// hit CORS for a third-party REST API.

switch ($f){
    case "GetEchoViaPhp":
        $returnObject = $a->hello == null ? "Hello Echo." : $a->hello;
        die(new JsonResponse($returnObject));
        break;
    case "GetPokemon":
        $aNameOrId    = $a->nameOrId;
        $returnObject = GetPokemon($aNameOrId);
        die(new JsonResponse($returnObject));
        break;
    case "SearchLibraryByNameViaPhp":
        $aSearch      = $a->search;
        $returnObject = SearchLibraryByNameViaPhp($aSearch);
        die(new JsonResponse($returnObject));
        break;
}
