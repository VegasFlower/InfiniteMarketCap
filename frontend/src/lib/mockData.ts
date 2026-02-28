export const overview = {
  totalMarketCap: "$53.2T",
  top5Share: "31.8%",
  top10Share: "47.2%",
  advancersRatio: "56%",
};

export const watchlist = [
  { symbol: "GOLD", name: "Gold", marketCap: "$20.1T", rank: 1, trend: 61 },
  { symbol: "BTC", name: "Bitcoin", marketCap: "$1.72T", rank: 8, trend: 82 },
  { symbol: "ETH", name: "Ethereum", marketCap: "$410B", rank: 31, trend: 73 },
  { symbol: "NVDA", name: "NVIDIA", marketCap: "$2.84T", rank: 4, trend: 79 },
];

export const anomalies = [
  { symbol: "BTC", title: "Trend acceleration", detail: "30D strength and rank momentum are both improving.", severity: "P1" },
  { symbol: "NVDA", title: "Return spike", detail: "30D return crossed anomaly threshold.", severity: "P2" },
];
