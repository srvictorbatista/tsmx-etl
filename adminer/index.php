<?php
/** Adminer Plugin - Define o padrão de conexão para PostgreSQL
 * Define os valores padrão para:
 * - Sistema: PostgreSQL
 * - Servidor: localhost
 * - Banco de dados: tsmx_etl
 *
 * Este plugin foi adaptado a partir da documentação oficial e preenche automaticamente e oculta os campos de login para sistema (driver) e servidor.
 * Para utilizá-lo, inclua a função a seguir no arquivo PHP do Adminer, diretamente ou por meio de include().
 * @autor Sr. Victor Batista
 * @git https://github.com/srvictorbatista
 * @link https://www.adminer.org/pt-br/plugins/#use
 * @licença https://www.apache.org/licenses/LICENSE-2.0 Licença Apache 2.0
 * @versão Plugin personalizado para Adminer 4.8.1
 */

// Ativa exibição de erros para facilitar o debug
#ini_set('display_errors', 1);ini_set('display_startup_errors', 1);error_reporting(E_ALL);

// Definição de valores padrão para a conexão
$valuesDefaults = [
    "driver" => "PostgreSQL",
    "server" => "localhost", //:5432",
    "username" => "postgres",
    "password" => "postgres",
    "db" => "tsmx_etl"
];

// Função que cria a classe personalizada do Adminer
function adminer_object(){
    global $valuesDefaults;
    return new class extends Adminer{
        function credentials() {
            global $valuesDefaults;
            return [
                $valuesDefaults['server'] ?? 'localhost', 
                $valuesDefaults['username'] ?? '', 
                $valuesDefaults['password'] ?? ''
            ];
        }

        function database() {
            global $valuesDefaults;
            return $valuesDefaults['db'] ?? '';
        }
        function loginFormField($n, $h, $v) {
            global $valuesDefaults;
            if ($n == 'driver') {
                return isset($valuesDefaults['driver']) && strtolower($valuesDefaults['driver']) == 'postgresql'
                    ? "<input type='hidden' name='auth[driver]' value='pgsql'>{$h}".h($valuesDefaults['driver'])."<td>"
                    : "{$h}" . $v;
            }
            if ($n == 'server') {
                return isset($valuesDefaults['server'])
                    ? "<input type='hidden' name='auth[server]' value='" . h($valuesDefaults['server']) . "'>{$h}" . h($valuesDefaults['server']) . "<td>"
                    : "{$h}" . $v;
            }
            if ($n == 'username') {
                return isset($valuesDefaults['username'])
                    ? "<input type='hidden' name='auth[username]' value='" . h($valuesDefaults['username']) . "'>{$h}" . h($valuesDefaults['username'])
                    : "{$h}" . $v;
            }
            if ($n == 'password') {
                return isset($valuesDefaults['password'])
                    ? "<input type='hidden' name='auth[password]' value='" . h($valuesDefaults['password']) . "'>{$h} ▉▉▉▉▉▉"
                    : "{$h}" . $v;
            }
            if ($n == 'db') {
                return isset($valuesDefaults['db'])
                    ? "<input type='hidden' name='auth[db]' value='" . h($valuesDefaults['db']) . "'>{$h}" . h($valuesDefaults['db'])
                    : "{$h}" . $v;
            }
            return $v;
        }
            
        function csp(){ return []; }
        function head(){
            echo '
            <script>
                window.addEventListener(\'load\', function(){
                    // Função enviar o formulário
                    function enviar(){
                        document.querySelector(\'*[method="post"] *[type="submit"]\').click();
                    }

                    // Verifica se há algum erro
                    if(document.querySelector(\'.error\')){
                        // Se encontrar, aguarda 30 segundos antes de enviar novamente
                        setTimeout(enviar, 30000); // 30 segundos
                        return;
                    }

                    // Verifica se ha credenciais disponiveis
                    if(document.querySelectorAll(\'tr\')[3].innerText.includes(\'▉\')){
                        setTimeout(enviar, 10); // 0.01 segundos
                    }
                });
            </script>
            <link rel="stylesheet" type="text/css" href="adminer.css?v='.time().'">';
        }
    };

}

// Inclui o arquivo mais recente do Adminer (4.9.0 ou mais antigo)
include(array_reduce(array_filter(glob("adminer-*.php"), fn($f) => preg_match('/adminer-(\d+\.\d+\.\d+)\.php$/', $f, $m) && version_compare($m[1], '4.9.0', '<=')), fn($a, $b) => @filemtime($a) > @filemtime($b) ? $a : $b));