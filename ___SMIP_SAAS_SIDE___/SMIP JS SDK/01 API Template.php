<?php

// Purpose: this script is a generic PHP API dispatch skeleton for any
// SMIP-side script that wants to expose server-side functions to the
// browser (or to other scripts) via tiqJSHelper.invokeScriptAsync().
//
// The pattern is a simple switch on $context->std_inputs->method:
//   - $f          — the requested function name (e.g. "MyTenantMethod")
//   - $a          — the parsed arguments object (from JSON in std_inputs->data)
//   - JsonResponse — Joomla's JSON envelope used to return values to the caller
//
// Tenant-specific libraries that want their own PHP-side methods should
// either fork this template into their own api_template script, or
// `includeScript` it and add `case "<MethodName>":` blocks to the switch
// below. The skeleton here ships with no cases — SMIP JS SDK is JS-only
// (mutations + getTypes); PHP cases are the tenant's to fill in.

require_once 'thinkiq_context.php';
$context = new Context();

TiqUtilities\Model\Script::includeScript('smip_js_sdk.guzzle_client');

use Joomla\CMS\Response\JsonResponse; // Used for returning data to the client.
if (!defined('JPATH_BASE')) define('JPATH_BASE', dirname(__DIR__));

$f = isset($context->std_inputs->method) ? $context->std_inputs->method : '';
$a = isset($context->std_inputs->data)   ? json_decode($context->std_inputs->data) : '';

use TiqUtilities\GraphQL\GraphQL;

// ---------------------------------------------------------------------
// Tenant-specific PHP-side functions go here. Define them above and
// add a matching `case "<MethodName>":` block to the switch below.
//
// Example (commented out — copy & adjust):
//
// function MyTenantMethod($someArg){
//     $client = new Guzzler();
//     return $client->GetAsync("some/path/$someArg");
// }
// ---------------------------------------------------------------------

switch ($f){
    // case "MyTenantMethod":
    //     $returnObject = MyTenantMethod($a->someArg);
    //     die(new JsonResponse($returnObject));
    //     break;
}
