# Easy exhibit: simple process message. Teaches BEAM basics.
defmodule EasyActor do
  def main do
    pid = spawn(fn ->
      receive do
        {:ping, from} -> send(from, :pong)
      end
    end)
    send(pid, {:ping, self()})
    receive do
      :pong -> IO.puts("easy_actor: ok")
    after
      1000 -> raise "timeout"
    end
  end
end

EasyActor.main()
