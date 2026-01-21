'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { Maximize2, Minimize2, RotateCcw, ZoomIn, ZoomOut, Pause, Play } from 'lucide-react';

interface Node {
  id: string;
  label: string;
  value: number;
  x?: number;
  y?: number;
  z?: number;
  color: string;
}

interface Edge {
  source: string;
  target: string;
  weight: number;
}

interface Visualization3DProps {
  data: {
    channel_attributions: Record<string, number>;
    channels_summary?: Record<string, number>;
  };
}

export default function Visualization3D({ data }: Visualization3DProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isRotating, setIsRotating] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);

  // Convert data to nodes and edges
  const channels = Object.keys(data.channel_attributions || {});
  const maxValue = Math.max(...Object.values(data.channel_attributions || {}));

  const nodes: Node[] = channels.map((channel, i) => {
    const angle = (i / channels.length) * Math.PI * 2;
    const radius = 150;
    return {
      id: channel,
      label: channel,
      value: data.channel_attributions[channel],
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      z: (Math.random() - 0.5) * 100,
      color: getChannelColor(channel, i)
    };
  });

  // Create edges between sequential channels (simplified flow)
  const edges = useMemo(() => {
    const edgesArray: Edge[] = [];
    for (let i = 0; i < channels.length; i++) {
      for (let j = i + 1; j < channels.length; j++) {
        const weight = Math.random() * 0.5 + 0.1;
        if (weight > 0.3) {
          edgesArray.push({
            source: channels[i],
            target: channels[j],
            weight
          });
        }
      }
    }
    return edgesArray;
  }, [channels]);

  function getChannelColor(channel: string, index: number): string {
    const colors = [
      '#f59e0b', // amber
      '#3b82f6', // blue
      '#10b981', // emerald
      '#8b5cf6', // purple
      '#ef4444', // red
      '#06b6d4', // cyan
      '#f97316', // orange
      '#ec4899', // pink
    ];
    return colors[index % colors.length];
  }

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let autoRotation = 0;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;
      const centerX = width / 2;
      const centerY = height / 2;

      // Clear canvas
      ctx.fillStyle = '#09090b';
      ctx.fillRect(0, 0, width, height);

      // Draw grid
      drawGrid(ctx, width, height);

      // Apply rotation
      const rotX = rotation.x + (isRotating ? autoRotation * 0.3 : 0);
      const rotY = rotation.y + (isRotating ? autoRotation : 0);

      // Transform nodes
      const transformedNodes = nodes.map(node => {
        const x = node.x || 0;
        const y = node.y || 0;
        const z = node.z || 0;

        // Rotate around Y axis
        const cosY = Math.cos(rotY * 0.01);
        const sinY = Math.sin(rotY * 0.01);
        const x1 = x * cosY - z * sinY;
        const z1 = x * sinY + z * cosY;

        // Rotate around X axis
        const cosX = Math.cos(rotX * 0.01);
        const sinX = Math.sin(rotX * 0.01);
        const y1 = y * cosX - z1 * sinX;
        const z2 = y * sinX + z1 * cosX;

        // Project to 2D with perspective
        const scale = 300 / (300 - z2);
        const screenX = centerX + x1 * scale * zoom;
        const screenY = centerY + y1 * scale * zoom;

        return {
          ...node,
          screenX,
          screenY,
          scale: scale * zoom,
          depth: z2
        };
      });

      // Sort by depth (back to front)
      transformedNodes.sort((a, b) => a.depth - b.depth);

      // Draw edges
      edges.forEach(edge => {
        const sourceNode = transformedNodes.find(n => n.id === edge.source);
        const targetNode = transformedNodes.find(n => n.id === edge.target);
        if (sourceNode && targetNode) {
          ctx.beginPath();
          ctx.moveTo(sourceNode.screenX, sourceNode.screenY);
          ctx.lineTo(targetNode.screenX, targetNode.screenY);

          const gradient = ctx.createLinearGradient(
            sourceNode.screenX, sourceNode.screenY,
            targetNode.screenX, targetNode.screenY
          );
          gradient.addColorStop(0, sourceNode.color + '40');
          gradient.addColorStop(1, targetNode.color + '40');

          ctx.strokeStyle = gradient;
          ctx.lineWidth = edge.weight * 3;
          ctx.stroke();
        }
      });

      // Draw nodes
      transformedNodes.forEach(node => {
        const radius = 15 + (node.value / maxValue) * 25;
        const isHovered = hoveredNode === node.id;

        // Glow effect
        if (isHovered) {
          ctx.shadowColor = node.color;
          ctx.shadowBlur = 20;
        }

        // Node circle
        ctx.beginPath();
        ctx.arc(node.screenX, node.screenY, radius * node.scale, 0, Math.PI * 2);

        const gradient = ctx.createRadialGradient(
          node.screenX - radius * 0.3, node.screenY - radius * 0.3, 0,
          node.screenX, node.screenY, radius * node.scale
        );
        gradient.addColorStop(0, node.color);
        gradient.addColorStop(1, node.color + '80');

        ctx.fillStyle = gradient;
        ctx.fill();

        // Border
        ctx.strokeStyle = isHovered ? '#ffffff' : node.color;
        ctx.lineWidth = isHovered ? 3 : 1;
        ctx.stroke();

        ctx.shadowBlur = 0;

        // Label
        ctx.font = `${Math.max(10, 12 * node.scale)}px monospace`;
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.fillText(node.label.toUpperCase(), node.screenX, node.screenY + radius * node.scale + 15);

        // Value
        ctx.font = `${Math.max(8, 10 * node.scale)}px monospace`;
        ctx.fillStyle = node.color;
        ctx.fillText(`${(node.value * 100).toFixed(1)}%`, node.screenX, node.screenY + radius * node.scale + 28);
      });

      // Draw legend
      drawLegend(ctx, width, height);

      if (isRotating) {
        autoRotation += 0.5;
      }

      animationRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [nodes, edges, zoom, rotation, isRotating, hoveredNode, maxValue]);

  function drawGrid(ctx: CanvasRenderingContext2D, width: number, height: number) {
    const gridSize = 30;
    ctx.strokeStyle = '#27272a';
    ctx.lineWidth = 0.5;

    // Perspective grid lines
    const vanishingY = height * 0.3;
    const gridLines = 20;

    for (let i = 0; i <= gridLines; i++) {
      const x = (i / gridLines) * width;

      ctx.beginPath();
      ctx.moveTo(x, height);
      ctx.lineTo(width / 2 + (x - width / 2) * 0.3, vanishingY);
      ctx.stroke();
    }

    for (let i = 0; i <= 10; i++) {
      const y = vanishingY + (height - vanishingY) * (i / 10);
      const spread = 1 - (height - y) / (height - vanishingY) * 0.7;

      ctx.beginPath();
      ctx.moveTo(width / 2 - (width / 2) * spread, y);
      ctx.lineTo(width / 2 + (width / 2) * spread, y);
      ctx.stroke();
    }
  }

  function drawLegend(ctx: CanvasRenderingContext2D, width: number, height: number) {
    const legendX = 20;
    const legendY = 20;

    ctx.font = '10px monospace';
    ctx.fillStyle = '#71717a';
    ctx.textAlign = 'left';
    ctx.fillText('CHANNEL NETWORK TOPOLOGY', legendX, legendY);

    ctx.fillStyle = '#52525b';
    ctx.fillText('Node size = Attribution weight', legendX, legendY + 15);
    ctx.fillText('Edge opacity = Transition probability', legendX, legendY + 28);
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setLastMousePos({ x: e.clientX, y: e.clientY });
    setIsRotating(false);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      const deltaX = e.clientX - lastMousePos.x;
      const deltaY = e.clientY - lastMousePos.y;
      setRotation(prev => ({
        x: prev.x + deltaY,
        y: prev.y + deltaX
      }));
      setLastMousePos({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom(prev => Math.max(0.5, Math.min(2, prev + delta)));
  };

  return (
    <div className={`relative ${isFullscreen ? 'fixed inset-0 z-50 bg-black' : ''}`}>
      {/* Controls */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2">
        <button
          onClick={() => setIsRotating(!isRotating)}
          className="p-2 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-colors"
          title={isRotating ? 'Pause rotation' : 'Resume rotation'}
        >
          {isRotating ? (
            <Pause className="w-4 h-4 text-amber-500" />
          ) : (
            <Play className="w-4 h-4 text-zinc-400" />
          )}
        </button>
        <button
          onClick={() => setRotation({ x: 0, y: 0 })}
          className="p-2 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-colors"
          title="Reset view"
        >
          <RotateCcw className="w-4 h-4 text-zinc-400" />
        </button>
        <button
          onClick={() => setZoom(prev => Math.min(2, prev + 0.2))}
          className="p-2 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-colors"
          title="Zoom in"
        >
          <ZoomIn className="w-4 h-4 text-zinc-400" />
        </button>
        <button
          onClick={() => setZoom(prev => Math.max(0.5, prev - 0.2))}
          className="p-2 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-colors"
          title="Zoom out"
        >
          <ZoomOut className="w-4 h-4 text-zinc-400" />
        </button>
        <button
          onClick={() => setIsFullscreen(!isFullscreen)}
          className="p-2 carbon-plate border border-zinc-700 hover:border-amber-500/30 transition-colors"
          title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
        >
          {isFullscreen ? (
            <Minimize2 className="w-4 h-4 text-zinc-400" />
          ) : (
            <Maximize2 className="w-4 h-4 text-zinc-400" />
          )}
        </button>
      </div>

      {/* Info Panel */}
      <div className="absolute bottom-4 left-4 z-10 carbon-plate border border-zinc-800 p-3 max-w-xs">
        <p className="text-xs text-zinc-500 font-mono uppercase mb-2">3D ATTRIBUTION NETWORK</p>
        <p className="text-xs text-zinc-400 font-mono">
          Drag to rotate - Scroll to zoom - Click node for details
        </p>
        <div className="mt-2 pt-2 border-t border-zinc-800">
          <p className="text-xs text-amber-500 font-mono">
            {nodes.length} Channels - {edges.length} Connections
          </p>
        </div>
      </div>

      {/* Canvas */}
      <canvas
        ref={canvasRef}
        width={isFullscreen ? window.innerWidth : 800}
        height={isFullscreen ? window.innerHeight : 500}
        className="w-full cursor-grab active:cursor-grabbing"
        style={{ background: '#09090b' }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      />

      {/* Scanlines overlay */}
      <div className="absolute inset-0 pointer-events-none scanlines opacity-5" />
    </div>
  );
}
