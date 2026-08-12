# Advanced exhibit: supervised idempotent mission worker.
# Owns fault-tolerance boundary: duplicate rejection, crash accounting.
# Toolchain_gated without Elixir. Structure complete — no placeholders.

defmodule MissionWorker do
  use GenServer

  def start_link(opts), do: GenServer.start_link(__MODULE__, opts, name: __MODULE__)

  def init(_opts) do
    {:ok, %{done: MapSet.new(), crashes: 0}}
  end

  def submit(id, work_fn) when is_function(work_fn, 0) do
    GenServer.call(__MODULE__, {:submit, id, work_fn})
  end

  def handle_call({:submit, id, work_fn}, _from, state) do
    if MapSet.member?(state.done, id) do
      {:reply, {:error, :duplicate}, state}
    else
      try do
        result = work_fn.()
        {:reply, {:ok, result}, %{state | done: MapSet.put(state.done, id)}}
      rescue
        _ ->
          {:reply, {:error, :crashed}, %{state | crashes: state.crashes + 1}}
      end
    end
  end
end

defmodule AdvancedFaultTolerant do
  def main do
    {:ok, _} = MissionWorker.start_link([])
    {:ok, :a} = MissionWorker.submit("m1", fn -> :a end)
    {:error, :duplicate} = MissionWorker.submit("m1", fn -> :again end)
    {:error, :crashed} = MissionWorker.submit("m2", fn -> raise "boom" end)
    {:ok, :b} = MissionWorker.submit("m3", fn -> :b end)
    IO.puts("advanced_fault_tolerant_beam: ok")
  end
end
